from storage_client import upload_file, list_objects, BUCKET_RAW

with open("test_facture.txt", "w") as f:
    f.write("Facture test")

upload_file(BUCKET_RAW, "test/facture_001.txt", "test_facture.txt")
print(list_objects(BUCKET_RAW))  # doit afficher ['test/facture_001.txt']