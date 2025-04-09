from Blog.models import DWDino, DWUserDino, DWUser, DWAttack, User

def run():
    for user in User.objects.all():
        DWUser.objects.create(
            user = user,
            free_hatch = 10,
            arena_energy = 5
        )

    attack = DWAttack.objects.create(
    name = "Armor Slam",
    atk_mult_low = 1.2,
    atk_mult_high = 1.5,
    spe_effect = "Augmente la défense de l'équipe alliée de 20% pendant 3s. Cooldown de 5s"
    )

    dino = DWDino.objects.create(
        name = "Ankylosaurus",
        classe = "tank",
        base_hp = 10000,
        base_atk = 310,
        base_def = 260,
        base_spd = 0.9,
        base_crit = 0.08,
        base_crit_dmg = 1.6,
        attack = attack
    )

    attack = DWAttack.objects.create(
    name = "Spike Tail Sweep",
    atk_mult_low = 1.0,
    atk_mult_high = 1.3,
    spe_effect = "Renvoie 50% des dégats reçus lors de la prochaine attaque subie à l'attaquant"
    )

    dino = DWDino.objects.create(
        name = "Stegosaurus",
        classe = "tank",
        base_hp = 9500,
        base_atk = 280,
        base_def = 210,
        base_spd = 1.1,
        base_crit = 0.1,
        base_crit_dmg = 1.6,
        attack = attack
    )

    attack = DWAttack.objects.create(
    name = "Horned Charge",
    atk_mult_low = 1.3,
    atk_mult_high = 1.6,
    spe_effect = "Stun l'ennemi touché pendant 2 secondes"
    )

    dino = DWDino.objects.create(
        name = "Triceratops",
        classe = "tank",
        base_hp = 9800,
        base_atk = 290,
        base_def = 230,
        base_spd = 1.0,
        base_crit = 0.08,
        base_crit_dmg = 1.5,
        attack = attack
    )

    attack = DWAttack.objects.create(
    name = "Crushing Bite",
    atk_mult_low = 1.4,
    atk_mult_high = 1.7,
    spe_effect = "A 30% de chance d'ignorer la défense de la cible"
    )

    dino = DWDino.objects.create(
        name = "T-Rex",
        classe = "dps",
        base_hp = 7300,
        base_atk = 350,
        base_def = 170,
        base_spd = 1.1,
        base_crit = 0.16,
        base_crit_dmg = 1.9,
        attack = attack
    )

    attack = DWAttack.objects.create(
    name = "Rapid Slash",
    atk_mult_low = 0.35,
    atk_mult_high = 0.45,
    spe_effect = "Frappe 2 à 5 fois en une seule attaque"
    )

    dino = DWDino.objects.create(
        name = "Velociraptor",
        classe = "dps",
        base_hp = 7000,
        base_atk = 390,
        base_def = 120,
        base_spd = 1.5,
        base_crit = 0.2,
        base_crit_dmg = 2.2,
        attack = attack
    )

    attack = DWAttack.objects.create(
    name = "Bleeding Strike",
    atk_mult_low = 1.3,
    atk_mult_high = 1.7,
    spe_effect = "Applique le statut saignement à la cible pendant 3s. Cooldown de 5s"
    )

    dino = DWDino.objects.create(
        name = "Spinosaurus",
        classe = "dps",
        base_hp = 7200,
        base_atk = 370,
        base_def = 150,
        base_spd = 1.3,
        base_crit = 0.15,
        base_crit_dmg = 1.8,
        attack = attack
    )

    attack = DWAttack.objects.create(
    name = "Echoing Roar",
    atk_mult_low = 1.2,
    atk_mult_high = 1.4,
    spe_effect = "Augmente la vitesse de toute l'équipe alliée de 15% pendant 3s. Cooldown de 5s"
    )

    dino = DWDino.objects.create(
        name = "Parasaurolophus",
        classe = "support",
        base_hp = 9000,
        base_atk = 310,
        base_def = 190,
        base_spd = 1.1,
        base_crit = 0.1,
        base_crit_dmg = 1.7,
        attack = attack
    )

    attack = DWAttack.objects.create(
    name = "Venom Spit",
    atk_mult_low = 1.1,
    atk_mult_high = 1.3,
    spe_effect = "Empoisonne la cible pendant 3s. Cooldown de 5s"
    )

    dino = DWDino.objects.create(
        name = "Dilophosaurus",
        classe = "support",
        base_hp = 8800,
        base_atk = 280,
        base_def = 180,
        base_spd = 1.2,
        base_crit = 0.12,
        base_crit_dmg = 1.7,
        attack = attack
    )

    attack = DWAttack.objects.create(
    name = "Sky Dive",
    atk_mult_low = 1.2,
    atk_mult_high = 1.5,
    spe_effect = "Ce Dino a 60% de chance d'esquiver la prochaine attaque subie. Cooldown de 1,5s"
    )

    dino = DWDino.objects.create(
        name = "Pteranodon",
        classe = "support",
        base_hp = 8300,
        base_atk = 280,
        base_def = 180,
        base_spd = 1.5,
        base_crit = 0.18,
        base_crit_dmg = 1.9,
        attack = attack
    )