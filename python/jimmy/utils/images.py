from singleton import SingletonClass


async def get_pictures(picture_id: str):
    contentful = SingletonClass().contentful

    picture_url = contentful.asset(picture_id).url()

    buildUrl = str(picture_url[2:])

    return buildUrl
