# TODO - Bulk Balance Update Admin Feature

## 📋 Plan pour modification sommes TOUS utilisateurs
**Objectif :** Bouton "Modifier tous soldes" dans admin → form (fixe/ajout/pourcent) → update DB

**Information Gathered:**
- models.py : User.balance (float)
- app.py : admin() → users=User.query.all(), update_user() single POST
- admin.html : table + promo search + edit modal individuelle

**Plan détaillé :**
1. **templates/admin.html** : Section "Actions globales" après promo search
   - Form POST /admin/bulk-balance : radios (fixe/ajout/%rate), input montant, submit "Appliquer à tous"
2. **app.py** : Nouvelle route @admin_required POST /admin/bulk-balance
   ```
   users = User.query.all()
   action = request.form['action'] # 'set'|'add'|'percent'
   amount = float(request.form['amount'])
   for user in users:
       if action=='set': user.balance = amount
       elif action=='add': user.balance += amount  
       elif action=='percent': user.balance *= (1 + amount/100)
   db.session.commit()
   flash(f'{len(users)} soldes mis à jour')
   ```
3. **Sécurité** : JS confirm('Modifier TOUS soldes ?')

**Dependent files :** app.py, templates/admin.html, models.py (OK)

**Followup steps :**
- [x] 1. Ajouter TODO_bulk_balance.md
- [x] 2. Edit admin.html (HTML form)
- [x] 3. Edit app.py (nouvelle route)
- [ ] 4. Tester bulk update
- [ ] 5. Update TODO.md principal, completion

**Confirmer plan ? (oui/procéder)**

