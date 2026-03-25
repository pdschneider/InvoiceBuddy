# Utils/vars.py
import customtkinter as ctk


def create_vars(globals):
    globals.file_var = ctk.StringVar(value=globals.workbook)
    globals.logging_level_var = ctk.StringVar(value=globals.logging_level)
    globals.theme_var = ctk.StringVar(value=globals.active_theme)
    globals.history_var = ctk.StringVar(value=globals.history_path)
    globals.inbox_dir_var = ctk.StringVar(value=globals.inbox)
    globals.workbook_var = ctk.StringVar(value=globals.workbook)
    globals.sheet_invoices_var = ctk.StringVar(value=globals.sheet_invoices)
    globals.sheet_CreditCards_var = ctk.StringVar(value=globals.sheet_CreditCards)
    globals.sheet_PurchaseOrders_var = ctk.StringVar(value=globals.sheet_PurchaseOrders)
    globals.table_InvoiceTable_var = ctk.StringVar(value=globals.table_InvoiceTable)
    globals.table_CreditCards_var = ctk.StringVar(value=globals.table_CreditCards)
    globals.table_PurchaseOrders_var = ctk.StringVar(value=globals.table_PurchaseOrders)
    globals.invoice_starting_row_var = ctk.IntVar(value=globals.invoice_starting_row)
    globals.card_starting_row_var = ctk.IntVar(value=globals.card_starting_row)
    globals.po_starting_row_var = ctk.IntVar(value=globals.po_starting_row)
    globals.archive_path_var = ctk.StringVar(value=globals.archive)
    globals.invoice_starting_column_var = ctk.IntVar(value=globals.invoice_starting_column)
    globals.card_starting_column_var = ctk.IntVar(value=globals.card_starting_column)
    globals.po_starting_column_var = ctk.IntVar(value=globals.po_starting_column)

    # Component Vars
    globals.invoice_com_a_var = ctk.StringVar(value=globals.invoice_component_a)
    globals.invoice_com_b_var = ctk.StringVar(value=globals.invoice_component_b)
    globals.invoice_com_c_var = ctk.StringVar(value=globals.invoice_component_c)
    globals.invoice_com_d_var = ctk.StringVar(value=globals.invoice_component_d)

    globals.card_com_a_var = ctk.StringVar(value=globals.card_component_a)
    globals.card_com_b_var = ctk.StringVar(value=globals.card_component_b)
    globals.card_com_c_var = ctk.StringVar(value=globals.card_component_c)
    globals.card_com_d_var = ctk.StringVar(value=globals.card_component_d)

    globals.po_com_a_var = ctk.StringVar(value=globals.po_component_a)
    globals.po_com_b_var = ctk.StringVar(value=globals.po_component_b)
    globals.po_com_c_var = ctk.StringVar(value=globals.po_component_c)
    globals.po_com_d_var = ctk.StringVar(value=globals.po_component_d)
