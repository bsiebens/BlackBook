from django.urls import path

from .views import dashboard, profile, accounts, transactions, categories, budgets, paychecks

app_name = "blackbook"
urlpatterns = [
    path("", dashboard.dashboard, name="dashboard"),
    path("profile/", profile.profile, name="profile"),
    #
    #
    # Accounts
    path("accounts/add/", accounts.add_edit_account, name="accounts_add"),
    path("accounts/edit/<str:account_slug>/", accounts.add_edit_account, name="accounts_edit"),
    path("accounts/delete/", accounts.delete, name="accounts_delete"),
    path("accounts/<str:account_type>/", accounts.accounts, name="accounts_list"),
    path("accounts/<str:account_type>/<str:account_slug>/", accounts.accounts, name="accounts_view"),
    #
    #
    # Transactions
    path("transactions/", transactions.transactions, name="transactions"),
    path("transactions/add/", transactions.add_edit, name="transactions_add"),
    path("transactions/edit/<str:transaction_uuid>/", transactions.add_edit, name="transactions_edit"),
    path("transactions/delete/", transactions.delete, name="transactions_delete"),
    #
    #
    # Categories
    path("categories/", categories.categories, name="categories"),
    path("categories/add/", categories.categories, name="categories_add"),
    path("categories/edit/", categories.categories, name="categories_edit"),
    path("categories/delete/", categories.delete, name="categories_delete"),
    #
    #
    # Categories
    path("budgets/", budgets.budgets, name="budgets"),
    path("budgets/add/", budgets.budgets, name="budgets_add"),
    path("budgets/edit/", budgets.budgets, name="budgets_edit"),
    path("budgets/delete/", budgets.delete, name="budgets_delete"),
    #
    #
    # PayChecks
    path("paychecks/", paychecks.paychecks, name="paychecks"),
]
