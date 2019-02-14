from bravado.client import SwaggerClient


def main():
    client = SwaggerClient.from_url('https://esi.evetech.net/latest/swagger.json')

    characterName = "Apollo Arkwright"

    charResults = client.Search.get_search(
        search=characterName,
        categories=['character'],
        strict=True,
    ).result()['character']

    if len(charResults) <= 0:
        raise Exception("Character not found")

    characterId = charResults[0]  # assuming only one result
    charInfo = client.Character.get_characters_character_id(character_id=characterId).result()

    print("Name: %s" % (charInfo['name']))
    print("Gender: %s" % (charInfo['gender']))
    print("Bio: %s" % (charInfo['description']))


if __name__ == "__main__":
    main()
