# TODO: Supprimer barre de recherche admin

User request: Supprimer la barre "Rechercher utilisateur par mots-clés (email)" dans admin.html

- [x] 1. Remove HTML block (label + div.input-group + small) from admin.html
- [x] 2. Remove CSS rules for #promoSearch.is-valid and #searchFeedback
- [x] 3. Remove JS: performEmailSearch, showFeedback, all promoSearch handlers
- [ ] 4. Update TODO_admin_search_fix.md
- [ ] 5. Test: python app.py && check /admin (no bar, no JS errors)

**Note:** Search bar completely removed. DataTables built-in search box remains available. Edit modal and other features intact.

