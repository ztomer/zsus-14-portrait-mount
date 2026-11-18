# Chtulhu Statue, by ChurchOfShrike

- Source: "Chtulhu Statue" by **ChurchOfShrike**, MakerWorld model 1705652
  (https://makerworld.com/en/models/1705652-chtulhu-statue), released 2025-08-16.
- Licence: **Creative Commons Attribution** (CC BY), as stated on the model page and in the file's own metadata.
- `Chtulhu_Statue_by_ChurchOfShrike.stl` is the statue mesh exactly as published, taken out of the downloaded 3MF
  (the designer's photos and print settings are not included).
- Changes made here: `CAD/make_relief.py` (recipe `CAD/emblems/cthulhu.json`) depth-casts the statue from the front,
  keeps only the head and its tentacle beard, and compresses it into a 1.2 mm bas-relief, which `CAD/build_emblem.py`
  joins to the snap-in chin emblem tile (`STLs/Part_B_Emblem_Cthulhu.stl`). The designer made the statue with
  MakerWorld's image-to-3D tool from a photo of a Cthulhu statue.
