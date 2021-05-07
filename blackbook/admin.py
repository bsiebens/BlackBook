from django.contrib import admin
from django.utils.html import format_html

from totalsum.admin import TotalsumAdmin

from . import models
from .utilities import format_iban


@admin.register(models.UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    def get_name(self, obj):
        return obj.user.get_full_name()

    get_name.short_description = "Name"

    list_display = ["user", "get_name", "default_currency", "created", "modified"]
    ordering = ["user"]
    search_fields = ["user", "uuid"]
    raw_id_fields = ["user"]
    fieldsets = [
        ["General information", {"fields": ["user", "default_currency"]}],
    ]


class TransactionInline(admin.TabularInline):
    model = models.Transaction
    extra = 0
    fields = ["uuid", "account", "amount", "foreign_amount", "created", "modified"]
    readonly_fields = fields


@admin.register(models.TransactionJournal)
class TransactionJournalAdmin(admin.ModelAdmin):
    ordering = ["date"]
    date_hierarchy = "date"
    list_display = ["uuid", "short_description", "date", "amount", "type", "created", "modified"]
    search_fields = ["uuid", "short_description", "description"]
    fieldsets = [
        [
            "General information",
            {"fields": ["date", "short_description", "description", "type", "category", "budget"]},
        ],
        ["Options", {"fields": ["uuid"]}],
    ]
    list_filter = ["type"]
    readonly_fields = ["uuid"]
    inlines = [TransactionInline]


@admin.register(models.Account)
class AccountAdmin(admin.ModelAdmin):
    def display_iban(self, obj):
        return format_iban(obj.iban)

    display_iban.short_description = "IBAN"

    ordering = ["name"]
    list_display = [
        "name",
        "slug",
        "type",
        "display_iban",
        "currency",
        "active",
        "net_worth",
        "dashboard",
        "virtual_balance",
        "balance",
        "uuid",
        "created",
        "modified",
    ]
    list_filter = ["type", "active", "net_worth", "dashboard", "currency"]
    search_fields = ["name", "uuid", "iban"]
    fieldsets = [
        ["General information", {"fields": ["name", "iban", "slug", "type", "icon", "currency"]}],
        ["Options", {"fields": ["active", "net_worth", "dashboard", "virtual_balance", "uuid"]}],
    ]
    readonly_fields = ["slug", "icon", "uuid"]


@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    ordering = ["name"]
    list_display = ["name", "uuid", "created", "modified"]
    search_fields = ["name", "uuid"]
    fieldsets = [
        ["General information", {"fields": ["name", "uuid"]}],
    ]
    readonly_fields = ["uuid"]


class BudgetPeriodInline(admin.TabularInline):
    model = models.BudgetPeriod
    extra = 0
    fields = ["start_date", "end_date", "amount", "created", "modified"]
    readonly_fields = fields


@admin.register(models.Budget)
class BudgetAdmin(admin.ModelAdmin):
    ordering = ["name"]
    list_display = ["name", "active", "amount", "auto_budget", "auto_budget_period", "uuid", "created", "modified"]
    search_fields = ["name", "uuid"]
    list_filter = ["active", "auto_budget", "auto_budget_period"]
    fieldsets = [
        ["General information", {"fields": ["name"]}],
        ["Options", {"fields": ["active", "amount", "auto_budget", "auto_budget_period", "uuid"]}],
    ]
    inlines = [BudgetPeriodInline]
    readonly_fields = ["uuid"]


class PaycheckItemInline(admin.TabularInline):
    def item_type(self, obj):
        return obj.category.type

    def percentage(self, obj):
        return format_html("{obj.category.counterbalance_percentage}&nbsp;&percnt;".format(obj=obj))

    def counterbalance(self, obj):
        return obj.category.counterbalance

    counterbalance.boolean = True

    model = models.PayCheckItem
    extra = 0
    raw_id_fields = ["paycheck"]
    fields = ["paycheck", "category", "item_type", "amount", "counterbalance", "percentage", "created", "modified"]
    readonly_fields = ["item_type", "counterbalance", "percentage", "created", "modified"]


@admin.register(models.PayCheckItemCategory)
class PaycheckItemCategoryAdmin(admin.ModelAdmin):
    def percentage(self, obj):
        return format_html("{obj.counterbalance_percentage}&nbsp;&percnt;".format(obj=obj))

    ordering = ["name"]
    list_display = ["name", "type", "default_amount", "counterbalance", "percentage", "default"]
    search_fields = ["name"]
    list_filter = ["type", "counterbalance", "default"]


@admin.register(models.Paycheck)
class PaycheckAdmin(TotalsumAdmin):
    def format_date(self, obj):
        return obj.date.strftime("%b %Y")

    format_date.admin_order_field = "date"
    format_date.short_description = "date"

    ordering = ["date"]
    date_hierarchy = "date"
    list_display = ["format_date", "amount", "uuid", "created", "modified"]
    readonly_fields = ["amount", "created", "modified"]
    inlines = [PaycheckItemInline]
    fieldsets = [[None, {"fields": ("date", "amount")}], ["General information", {"fields": ("uuid",)}]]
    readonly_fields = ["uuid"]
    totalsum_list = ["amount"]
    unit_of_measure = "&euro;"


@admin.register(models.Bonus)
class BonusAdmin(TotalsumAdmin):
    def format_date(self, obj):
        return obj.date.strftime("%b %Y")

    format_date.admin_order_field = "date"
    format_date.short_description = "date"

    def show_percentage(self, obj):
        return format_html("{obj.tax_percentage}&nbsp;&percnt;".format(obj=obj))

    show_percentage.short_description = "tax percentage"

    ordering = ["date"]
    date_hierarchy = "date"
    list_display = ["format_date", "gross_amount", "net_amount", "taxes", "show_percentage", "created", "modified"]
    readonly_fields = ["taxes", "show_percentage", "created", "modified"]
    fieldsets = [
        [None, {"fields": ("date", "gross_amount", "net_amount", "taxes", "show_percentage")}],
        ["General information", {"fields": ("created", "modified")}],
    ]
    totalsum_list = ["gross_amount", "net_amount", "taxes"]
    unit_of_measure = "&euro;"