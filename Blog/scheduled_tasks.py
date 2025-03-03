import time


def test_task():
    print('ici')
    time.sleep(1)
    print("Bonjour Théophile !")


from Blog.models import User, Box, UserInventory, Item
def drop_lootbox(nb_box, nb_coin):

    users = User.objects.all()
    box_id = Box.objects.last().id
    for user in users:
        user.coins += nb_coin
        user.save()
        for _ in range(nb_box):
            UserInventory.objects.create(user=user, item=Item.objects.create(type='box', item_id=box_id))

    print(f'{nb_box} lootboxes dropped for each user | {nb_coin} coins added to each user')
