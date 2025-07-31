from app.features.characters.schemas import CharacterModel
from app.db.mongo import get_characters_collection
from app.utils.local_Image_handler import save_single_image, save_gallery_images

BASE_STORAGE_PATH = "../../../storage/characters"

async def create_character_controller(
    data: CharacterModel,
    avatar_file=None,
    background_file=None,
    gallery_files=None
) -> CharacterModel:
    collection = get_characters_collection()
    try:
        # Normalize name for uniqueness (case-insensitive, trimmed)

        normalized_name = data.name.strip()

        existing = await collection.find_one({"name": {"$regex": f"^{normalized_name}$", "$options": "i"}})
        if existing:
            raise ValueError("Character with this name already exists.")

        

         # 3. Handle image uploads
        avatar_path = None
        if avatar_file:
            avatar_path = await save_single_image(BASE_STORAGE_PATH, "avatar", avatar_file.name, avatar_file)
        
        background_path = None
        if background_file:
            background_path = await save_single_image(BASE_STORAGE_PATH,"backgroud",  background_file.filename, background_file)
        
        gallery_paths = []
        if gallery_files:
            gallery_paths = await save_gallery_images(BASE_STORAGE_PATH, gallery_files)
        
          # 4. Merge data with image paths
        updated_data = data.model_copy(update={
            "extensions": {
                **data.extensions.model_dump(),
                "avatar": avatar_path,
                "background_image": background_path,
                "gallery": gallery_paths
            }
        })
          # 5. Save to DB
        await collection.insert_one(updated_data.model_dump())

        return updated_data

    except ValueError:
        raise
    except Exception as e:
        raise Exception(f"Failed to create character: {e}")
