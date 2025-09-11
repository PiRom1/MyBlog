#!/usr/bin/env python3
"""
Script to populate the database with all PvM abilities and terrains in French.

This script will add all the abilities and terrains defined in the game logic
to the database. It can be run multiple times safely as it checks for existing
entries before creating new ones.

Usage: python manage.py runscript populate_pvm_data
"""

import os
import sys
import django

# Setup Django environment
sys.path.append('/home/runner/work/MyBlog/MyBlog')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MyBlog.settings')
django.setup()

from Blog.models import DWPvmAbility, DWPvmTerrain


def populate_abilities():
    """Populate the database with all PvM abilities in French."""
    
    # Team abilities (to_dino=False)
    team_abilities = [
        {
            'name': 'Dernier souffle',
            'description': 'Quand un allié meurt, les autres récupèrent 20% de leur PV immédiatement.',
            'to_dino': False
        },
        {
            'name': 'Sprint préhistorique',
            'description': '+15% de vitesse pour toute l\'équipe pendant les 5 premières secondes du combat.',
            'to_dino': False
        },
        {
            'name': 'Esprit de meute',
            'description': '+20% d\'attaque si tous les alliés sont vivants, -10% sinon.',
            'to_dino': False
        },
        {
            'name': 'Bouclier collectif',
            'description': '10% des dégâts reçus sont partagés équitablement entre tous les alliés vivants.',
            'to_dino': False
        },
        {
            'name': 'Instinct protecteur',
            'description': 'Quand un membre de l\'équipe subit un coup critique, toute l\'équipe gagne +20% de défense pendant 1 seconde.',
            'to_dino': False
        },
        {
            'name': 'Pression croissante',
            'description': 'Toutes les 3 secondes, l\'attaque de l\'équipe augmente de +5%.',
            'to_dino': False
        },
        {
            'name': 'Seul contre tous',
            'description': 'Si un seul dino reste vivant, il gagne +20% de défense.',
            'to_dino': False
        },
        {
            'name': 'Terreur collective',
            'description': 'Quand un ennemi meurt, toute l\'équipe gagne +8% d\'attaque de façon permanente.',
            'to_dino': False
        }
    ]
    
    # Individual dino abilities (to_dino=True)
    individual_abilities = [
        {
            'name': 'Mort-vivant',
            'description': 'Après la mort, continue d\'attaquer pendant 2 secondes sans pouvoir être ciblé (sauf si c\'est le dernier dino).',
            'to_dino': True
        },
        {
            'name': 'Frénésie',
            'description': '+20% de vitesse d\'attaque quand les PV sont inférieurs à 30%.',
            'to_dino': True
        },
        {
            'name': 'Boureau',
            'description': 'Exécution instantanée si les PV restants de la cible sont inférieurs aux dégâts infligés.',
            'to_dino': True
        },
        {
            'name': 'Peau dure',
            'description': '15% de réduction des dégâts quand les PV sont supérieurs à 70%.',
            'to_dino': True
        },
        {
            'name': 'Inspiration héroïque',
            'description': 'En cas de coup critique, tous les alliés gagnent +20% d\'attaque pendant 1 seconde.',
            'to_dino': True
        },
        {
            'name': 'Vol de vie',
            'description': 'Récupère 15% des dégâts infligés sous forme de PV après chaque attaque.',
            'to_dino': True
        },
        {
            'name': 'Provocation',
            'description': 'Ce dino a 2 fois plus de chances d\'être ciblé par les ennemis.',
            'to_dino': True
        },
        {
            'name': 'Agilitée accrue',
            'description': '20% de chance d\'esquiver les attaques quand ce dino est attaqué.',
            'to_dino': True
        },
        {
            'name': 'Regard pétrifiant',
            'description': '25% de chance à l\'attaque de réduire la vitesse de la cible de 50% pendant 3 secondes.',
            'to_dino': True
        },
        {
            'name': 'Régénération',
            'description': 'Toutes les 2 secondes, récupère 5% des PV maximum.',
            'to_dino': True
        },
        {
            'name': 'Chasseur nocturne',
            'description': '+30% de chance de coup critique contre les ennemis affectés par du poison ou des saignements.',
            'to_dino': True
        },
        {
            'name': 'Carapace robuste',
            'description': 'Commence chaque combat avec 90% de résistance aux dégâts. La résistance diminue de 20% à chaque coup reçu.',
            'to_dino': True
        }
    ]
    
    all_abilities = team_abilities + individual_abilities
    created_count = 0
    existing_count = 0
    
    print("=== Ajout des capacités PvM ===")
    
    for ability_data in all_abilities:
        ability, created = DWPvmAbility.objects.get_or_create(
            name=ability_data['name'],
            defaults={
                'description': ability_data['description'],
                'to_dino': ability_data['to_dino']
            }
        )
        
        if created:
            created_count += 1
            print(f"✅ Créée: {ability.name} ({'Individuelle' if ability.to_dino else 'Équipe'})")
        else:
            existing_count += 1
            print(f"⚠️  Existe déjà: {ability.name}")
    
    print(f"\n📊 Résumé des capacités:")
    print(f"   - Nouvelles capacités créées: {created_count}")
    print(f"   - Capacités déjà existantes: {existing_count}")
    print(f"   - Total: {DWPvmAbility.objects.count()} capacités dans la base de données")


def populate_terrains():
    """Populate the database with all PvM terrains in French."""
    
    terrains = [
        {
            'name': 'Distorsion',
            'description': 'Les statistiques des dinos sont mélangées de manière aléatoire, créant des combinaisons imprévisibles.'
        },
        {
            'name': 'Lac Putréfié',
            'description': 'Tous les dinos perdent 5% de leurs PV maximum chaque seconde, rendant les combats plus rapides et intenses.'
        },
        {
            'name': 'Brouillard Épais',
            'description': 'Réduit de 50% la précision de tous les dinos, augmentant les chances d\'esquive.'
        },
        {
            'name': 'Jungle Perfide',
            'description': 'Le cooldown des capacités est réduit de 20% pour les dinos de support, favorisant les stratégies d\'équipe.'
        },
        {
            'name': 'Ère Glaciaire',
            'description': 'Tous les dinos commencent le combat avec une vitesse de base de 1.0, égalisant les chances.'
        },
        {
            'name': 'Montagne Rocheuse',
            'description': '+10% de défense pour les dinos Tank, mais -20% d\'attaque pour les dinos DPS.'
        },
        {
            'name': 'Éruption Volcanique',
            'description': '+10% d\'attaque pour les dinos DPS, mais -20% de défense pour les dinos Tank.'
        }
    ]
    
    created_count = 0
    existing_count = 0
    
    print("\n=== Ajout des terrains PvM ===")
    
    for terrain_data in terrains:
        terrain, created = DWPvmTerrain.objects.get_or_create(
            name=terrain_data['name'],
            defaults={
                'description': terrain_data['description']
            }
        )
        
        if created:
            created_count += 1
            print(f"✅ Créé: {terrain.name}")
        else:
            existing_count += 1
            print(f"⚠️  Existe déjà: {terrain.name}")
    
    print(f"\n📊 Résumé des terrains:")
    print(f"   - Nouveaux terrains créés: {created_count}")
    print(f"   - Terrains déjà existants: {existing_count}")
    print(f"   - Total: {DWPvmTerrain.objects.count()} terrains dans la base de données")


def run():
    """Main function to populate both abilities and terrains."""
    print("🚀 Début du remplissage de la base de données PvM...")
    print("=" * 60)
    
    try:
        populate_abilities()
        populate_terrains()
        
        print("\n" + "=" * 60)
        print("✅ Remplissage terminé avec succès!")
        print(f"📋 Total final:")
        print(f"   - Capacités: {DWPvmAbility.objects.count()}")
        print(f"   - Terrains: {DWPvmTerrain.objects.count()}")
        
    except Exception as e:
        print(f"❌ Erreur lors du remplissage: {e}")
        raise


if __name__ == "__main__":
    run()