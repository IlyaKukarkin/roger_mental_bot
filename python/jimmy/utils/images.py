from singleton import SingletonClass


async def get_pictures(picture_id: str):
    contentful = SingletonClass().contentful

    url = contentful.asset(picture_id).url()

    buildUrl = str(url[2:]) + '?fm=jpg'

    return buildUrl
