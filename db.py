import os
import yaml
import pyodbc

# Custom Decorator
def run_once(func):
    def wrapper(*args, **kwargs):
        if not wrapper.has_run:
            wrapper.has_run = True
            return func(*args, **kwargs)
    wrapper.has_run = False
    return wrapper

@run_once
def initialize_schema(cursor):
    with open('schema.sql', 'r', encoding='utf-8') as file:
        sql_script = file.read()

    cursor.execute(sql_script)
    print("Schema infrastracture created.")

def load_class(cursor, yaml_path):
    with open(yaml_path, 'r', encoding='utf-8') as file:
        data = yaml.safe_load(file)

    classNames = data['names']

    if isinstance(classNames, dict):
        classNames = classNames.values()

    for classID, className in enumerate(classNames):
        cursor.execute(
            "{CALL dbo.InsertClass(?,?)}",
            (classID, className)
        )
    print("Classes loaded successfully.")

def load_dataset(cursor, dataset_dir):
    IMAGE_EXTENSION = ('.jpg', '.jpeg', '.png')

    # Correctly maps folder names
    SPLIT_ID = {
        'train': 0,
        'valid': 1,
        'test': 2,
    }

    # Enable for faster bulk inserts
    cursor.fast_executemany = True 
    
    # Collect image file paths and their corresponding label paths
    imageFiles = [] # (filePath, splitID)
    labelMap = {} 

    for splitName, splitID in SPLIT_ID.items():
        images_dir = os.path.join(dataset_dir, splitName, 'images')
        labels_dir = os.path.join(dataset_dir, splitName, 'labels')
 
        if not os.path.exists(images_dir): # Image folder doesn't exist
            continue
 
        for fileName in os.listdir(images_dir):
            if not fileName.lower().endswith(IMAGE_EXTENSION): 
                continue
 
            imagePath = os.path.join(images_dir, fileName) # Direct image filepath
            baseName = os.path.splitext(fileName)[0] # Base name without extension
            labelPath = os.path.join(labels_dir, baseName + '.txt') # Corresponding label filepath
 
            imageFiles.append((imagePath, splitID))
            labelMap[imagePath] = labelPath if os.path.exists(labelPath) else None
 
    if not imageFiles:
        print("No images found in the specified dataset path.")
        return

    # Check for existing images to avoid duplicates
    cursor.execute("SELECT filePath FROM Image")
    existing_paths = {row[0] for row in cursor.fetchall()}
 
    imageRows = [(path, splitId) for path, splitId in imageFiles if path not in existing_paths]
    skipped = len(imageFiles) - len(imageRows)
    if skipped:
        print(f"{skipped} images already present in the database.")
 
    if not imageRows:
        print("No new images to insert.")
        return
 
    # Bulk insert new images
    try:
        print(f"Inserting {len(imageRows)} new image records...")
        cursor.executemany(
            "INSERT INTO Image (filePath, splitID) VALUES (?, ?);",
            imageRows
        )
        cursor.connection.commit()

        # Read back the generated imageIDs
        cursor.execute(
            "SELECT imageID, filePath FROM Image WHERE filePath LIKE ?;",
            dataset_dir + '%'
        )
        imageIDPath = {filePath: imageID for imageID, filePath in cursor.fetchall()}
 
    except Exception as e:
        cursor.connection.rollback()
        raise RuntimeError(f"Image insert failed: {e}") from e
 
    # Parse YOLO .txt label files
    labelRows = []  # (imageID, classID, xCenter, yCenter, boxWidth, boxHeight)
    newPaths = {path for path, _ in imageRows}
 
    for imagePath in newPaths:
        labelPath = labelMap.get(imagePath)
        if labelPath is None:
            continue  # Image with no annotations
 
        imageID = imageIDPath.get(imagePath)
        if imageID is None:
            print(f"Warning: No imageID found for {imagePath}, skipping corresponding labels")
            continue
 
        with open(labelPath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split()
                classID = int(parts[0])
                xCenter, yCenter, boxWidth, boxHeight = (float(p) for p in parts[1:5])
                labelRows.append((imageID, classID, xCenter, yCenter, boxWidth, boxHeight))
 
    # Bulk insert labels
    if labelRows:
        try:
            print(f"Inserting {len(labelRows)} label records...")
            cursor.executemany(
                """
                INSERT INTO Label (imageID, classID, xCenter, yCenter, boxWidth, boxHeight)
                VALUES (?, ?, ?, ?, ?, ?);
                """,
                labelRows
            )
            cursor.connection.commit()
            print("Database upload successfully completed!")
        except Exception as e:
            cursor.connection.rollback()
            raise RuntimeError(f"Label insert failed: {e}") from e
    else:
        print("Images inserted, but no label files were found.")