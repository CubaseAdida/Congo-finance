# TODO: Compte bloqué + Flow d'activation

**Statut:** [COMPLETÉ]

## Modifications apportées:
- `models.py`: `is_blocked default=True`
- `app.py/register()`: `user.is_blocked = True` explicite
- `templates/dashboard.html`: Section "Commencer à investir" si bloqué (instructions 1500 FCFA → WhatsApp +242050542421)
- `templates/deposit.html`: Label "Dépôt d'activation (1500 FCFA)"
- `app.py/deposit()`: Vérif exact 1500 FCFA, message WhatsApp

## Flux complet:
1. ✅ Inscription → compte bloqué par défaut
2. ✅ Login → voit "Commencer à investir" au dashboard
3. ✅ Clic → deposit page avec instructions WhatsApp
4. ✅ Admin reçoit preuve → débloque via admin panel (bouton existant)

**Test:** `cd investment_site && python app.py`
- Créer nouveau compte → bloqué
- Dashboard montre activation flow
- Deposit force 1500 FCFA
- Admin peut débloquer

**Admin:** Login admin@congofinance.com/admin2024 → toggle block.

