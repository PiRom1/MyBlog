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

# Setup Django environment (works both with manage.py runscript and direct run)
try:
    import django  # type: ignore
    if not os.environ.get('DJANGO_SETTINGS_MODULE'):
        # Assume project is at MyBlog/MyBlog
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MyBlog.settings')
    django.setup()
except Exception:
    # In case this script is executed via manage.py runscript, the environment is already set
    pass

from Blog.models import DWPvmAbility, DWPvmTerrain
from django.db import transaction


def populate_abilities():
    """Populate the database with all PvM abilities in French."""
    
    # Team abilities (to_dino=False)
    team_abilities = [
        {
            'name': 'Mort-vivant',
            'description': 'Quand le premier allié meurt, il continue d\'attaquer pendant 2 secondes sans pouvoir être ciblé.',
            'to_dino': False
        },
        {
            'name': 'Dernier souffle',
            'description': 'Quand un allié meurt, les autres récupèrent 20% de leur PV immédiatement.',
            'to_dino': False
        },
        {
            'name': 'Sprint préhistorique',
            'description': '+20% de vitesse pour toute l\'équipe pendant les 5 premières secondes du combat.',
            'to_dino': False
        },
        {
            'name': 'Esprit de meute',
            'description': '+20% d\'attaque si tous les alliés sont vivants, -10% sinon.',
            'to_dino': False
        },
        {
            'name': 'Bouclier collectif',
            'description': '50% des dégâts reçus sont partagés équitablement entre tous les autres alliés vivants.',
            'to_dino': False
        },
        {
            'name': 'Instinct protecteur',
            'description': 'Quand un membre de l\'équipe subit un coup critique, toute l\'équipe gagne +30% de défense pendant 2 secondes.',
            'to_dino': False
        },
        {
            'name': 'Pression croissante',
            'description': 'Toutes les 3 secondes, l\'attaque de l\'équipe augmente de +5%.',
            'to_dino': False
        },
        {
            'name': 'Seul contre tous',
            'description': 'S\'il ne reste qu\'un seul allié vivant, il gagne +25% dans toutes les statistiques.',
            'to_dino': False
        },
        {
            'name': 'Terreur collective',
            'description': 'Quand un ennemi meurt, toute l\'équipe gagne +15% d\'attaque pour le reste du combat.',
            'to_dino': False
        }
    ]
    
    # Individual dino abilities (to_dino=True)
    individual_abilities = [
        {
            'name': 'Frénésie',
            'description': '+25% de vitesse d\'attaque quand les PV sont inférieurs à 50%.',
            'to_dino': True
        },
        {
            'name': 'Bourreau',
            'description': 'Plus les PV de la cible sont bas, plus cette dino a de chances de la tuer instantanément (((1-PV restants/PV totaux)^4)/1.5).',
            'to_dino': True
        },
        {
            'name': 'Peau dure',
            'description': '20% de réduction des dégâts quand les PV sont supérieurs à 50%.',
            'to_dino': True
        },
        {
            'name': 'Inspiration héroïque',
            'description': 'En cas de coup critique, tous les alliés gagnent +25% d\'attaque pendant 1 seconde.',
            'to_dino': True
        },
        {
            'name': 'Vol de vie',
            'description': 'Récupère 30% des dégâts infligés sous forme de PV après chaque attaque.',
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
            'description': 'Après avoir attaqué, réduit la vitesse de la cible de 25% pendant 3 secondes.',
            'to_dino': True
        },
        {
            'name': 'Régénération',
            'description': 'Toutes les 2 secondes, récupère 5% des PV maximum.',
            'to_dino': True
        },
        {
            'name': 'Chasseur nocturne',
            'description': 'Inflige 2x les dégâts contre les ennemis affectés par du poison ou des saignements.',
            'to_dino': True
        },
        {
            'name': 'Carapace robuste',
            'description': 'Commence chaque combat avec 50% de réduction des dégâts. La réduction diminue de 3% à chaque coup reçu (minimum -25%).',
            'to_dino': True
        },
        {
            'name': 'Boost de vie',
            'description': 'Au début du combat, augmente les PV maximum de 20%.',
            'to_dino': True
        },
        {
            'name': 'Boost d\'attaque',
            'description': 'Au début du combat, augmente l\'attaque de 20%.',
            'to_dino': True
        },
        {
            'name': 'Boost de défense',
            'description': 'Au début du combat, augmente la défense de 20%.',
            'to_dino': True
        },
        {
            'name': 'Boost de vitesse',
            'description': 'Au début du combat, augmente la vitesse de 20%.',
            'to_dino': True
        },
        {
            'name': 'Boost de % critique',
            'description': 'Au début du combat, augmente les chances de coup critique de 0.1.',
            'to_dino': True
        },
        {
            'name': 'Boost de dégâts critiques',
            'description': 'Au début du combat, augmente les dégâts critiques de 30%.',
            'to_dino': True
        }
    ]
    
    all_abilities = team_abilities + individual_abilities
    created_count = 0
    updated_count = 0
    unchanged_count = 0
    
    print("=== Ajout des capacités PvM ===")
    
    with transaction.atomic():
        for ability_data in all_abilities:
            ability = DWPvmAbility.objects.filter(name=ability_data['name']).first()
            if ability is None:
                # Create new ability
                ability = DWPvmAbility.objects.create(
                    name=ability_data['name'],
                    description=ability_data['description'],
                    to_dino=ability_data['to_dino']
                )
                created_count += 1
                print(f"✅ Créée: {ability.name} ({'Individuelle' if ability.to_dino else 'Équipe'})")
            else:
                changed_fields = []
                if ability.description != ability_data['description']:
                    ability.description = ability_data['description']
                    changed_fields.append('description')
                if ability.to_dino != ability_data['to_dino']:
                    ability.to_dino = ability_data['to_dino']
                    changed_fields.append('to_dino')
                if changed_fields:
                    ability.save(update_fields=changed_fields)
                    updated_count += 1
                    print(f"🔄 Mis à jour: {ability.name} -> {', '.join(changed_fields)}")
                else:
                    unchanged_count += 1
                    print(f"⏭️  Inchangée: {ability.name}")
    
    print(f"\n📊 Résumé des capacités:")
    print(f"   - Nouvelles capacités créées: {created_count}")
    print(f"   - Capacités mises à jour: {updated_count}")
    print(f"   - Capacités inchangées: {unchanged_count}")
    print(f"   - Total: {DWPvmAbility.objects.count()} capacités dans la base de données")


def populate_terrains():
    """Populate the database with all PvM terrains in French."""
    
    terrains = [
        {
            'name': 'Distorsion Spatio-Temporelle',
            'description': 'Les statistiques des dinos sont mélangées de manière aléatoire entre tous les dinos.'
        },
        {
            'name': 'Lac Putréfié',
            'description': 'Tous les dinos perdent 5% de leurs PV maximum chaque seconde.'
        },
        {
            'name': 'Brouillard Epais',
            'description': 'Réduit de 50% la précision de tous les dinos.'
        },
        {
            'name': 'Jungle Perfide',
            'description': 'Le cooldown des capacités est réduit de 20% pour les dinos de support.'
        },
        {
            'name': 'Ere Glaciaire',
            'description': 'Tous les dinos ont une vitesse de base de 1.0.'
        },
        {
            'name': 'Montagne Rocheuse',
            'description': '+10% de défense pour les dinos Tank, mais -20% d\'attaque pour les dinos DPS.'
        },
        {
            'name': 'Eruption Volcanique',
            'description': '+10% d\'attaque pour les dinos DPS, mais -20% de défense pour les dinos Tank.'
        }
    ]
    
    created_count = 0
    updated_count = 0
    unchanged_count = 0
    
    print("\n=== Ajout des terrains PvM ===")
    
    with transaction.atomic():
        for terrain_data in terrains:
            terrain = DWPvmTerrain.objects.filter(name=terrain_data['name']).first()
            if terrain is None:
                terrain = DWPvmTerrain.objects.create(
                    name=terrain_data['name'],
                    description=terrain_data['description']
                )
                created_count += 1
                print(f"✅ Créé: {terrain.name}")
            else:
                changed_fields = []
                if terrain.description != terrain_data['description']:
                    terrain.description = terrain_data['description']
                    changed_fields.append('description')
                if changed_fields:
                    terrain.save(update_fields=changed_fields)
                    updated_count += 1
                    print(f"🔄 Mis à jour: {terrain.name} -> {', '.join(changed_fields)}")
                else:
                    unchanged_count += 1
                    print(f"⏭️  Inchangé: {terrain.name}")
    
    print(f"\n📊 Résumé des terrains:")
    print(f"   - Nouveaux terrains créés: {created_count}")
    print(f"   - Terrains mis à jour: {updated_count}")
    print(f"   - Terrains inchangés: {unchanged_count}")
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