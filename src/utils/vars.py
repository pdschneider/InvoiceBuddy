# src/utils/vars.py
import customtkinter as ctk


def create_vars(globs):
    globs.file_var = ctk.StringVar(value=globs.workbook)
    globs.logging_level_var = ctk.StringVar(value=globs.logging_level)
    globs.theme_var = ctk.StringVar(value=globs.active_theme)
    globs.history_var = ctk.StringVar(value=globs.history_path)
    globs.inbox_dir_var = ctk.StringVar(value=globs.inbox)
    globs.workbook_var = ctk.StringVar(value=globs.workbook)
    globs.sheet_invoices_var = ctk.StringVar(value=globs.sheet_invoices)
    globs.sheet_CreditCards_var = ctk.StringVar(value=globs.sheet_CreditCards)
    globs.sheet_PurchaseOrders_var = ctk.StringVar(value=globs.sheet_PurchaseOrders)
    globs.table_InvoiceTable_var = ctk.StringVar(value=globs.table_InvoiceTable)
    globs.table_CreditCards_var = ctk.StringVar(value=globs.table_CreditCards)
    globs.table_PurchaseOrders_var = ctk.StringVar(value=globs.table_PurchaseOrders)
    globs.invoice_starting_row_var = ctk.IntVar(value=globs.invoice_starting_row)
    globs.card_starting_row_var = ctk.IntVar(value=globs.card_starting_row)
    globs.po_starting_row_var = ctk.IntVar(value=globs.po_starting_row)
    globs.archive_path_var = ctk.StringVar(value=globs.archive)
    globs.invoice_starting_column_var = ctk.IntVar(value=globs.invoice_starting_column)
    globs.card_starting_column_var = ctk.IntVar(value=globs.card_starting_column)
    globs.po_starting_column_var = ctk.IntVar(value=globs.po_starting_column)
    globs.default_printer_var = ctk.StringVar(value=globs.default_printer)
    globs.github_check_var = ctk.BooleanVar(value=globs.github_check)
    globs.beta_var = ctk.BooleanVar(value=globs.beta)
    globs.dynamic_window_size_var = ctk.BooleanVar(value=globs.dynamic_window_size)
    globs.legacy_mode_var = ctk.BooleanVar(value=globs.legacy_mode)

    # Component Vars
    globs.invoice_com_a_var = ctk.StringVar(value=globs.invoice_component_a)
    globs.invoice_com_b_var = ctk.StringVar(value=globs.invoice_component_b)
    globs.invoice_com_c_var = ctk.StringVar(value=globs.invoice_component_c)
    globs.invoice_com_d_var = ctk.StringVar(value=globs.invoice_component_d)

    globs.card_com_a_var = ctk.StringVar(value=globs.card_component_a)
    globs.card_com_b_var = ctk.StringVar(value=globs.card_component_b)
    globs.card_com_c_var = ctk.StringVar(value=globs.card_component_c)
    globs.card_com_d_var = ctk.StringVar(value=globs.card_component_d)

    globs.po_com_a_var = ctk.StringVar(value=globs.po_component_a)
    globs.po_com_b_var = ctk.StringVar(value=globs.po_component_b)
    globs.po_com_c_var = ctk.StringVar(value=globs.po_component_c)
    globs.po_com_d_var = ctk.StringVar(value=globs.po_component_d)
