from singleton import SingletonClass


async def get_pictures(picture_id: str):
    contentful = SingletonClass().contentful

    url = contentful.asset(picture_id).url()

    return str(url[2:])
