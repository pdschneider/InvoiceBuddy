# Interface/Settings/spreadsheet_settings.py
import customtkinter as ctk
import Utils.fonts as fonts
from Utils.save_settings import save_all_settings

def create_spreadsheet_settings_tab(globals, spreadsheet_tab):
    """
    Create the Settings tab for configuring paths and advanced settings.

    Args:
        globals (globals): The global configuration object containing UI variables and settings.
    """
    ctk.CTkLabel(spreadsheet_tab, 
                font=fonts.title_font,
                text="Spreadsheet").pack(pady=20, fill="x", anchor="center", padx=10)

    # Invoices
    ctk.CTkLabel(spreadsheet_tab, 
                font=fonts.title_font,
                text="Invoices").pack(pady=20, fill="x", anchor="center", padx=10)
    
    # Invoice Paths Frame
    invoice_paths_section = ctk.CTkFrame(spreadsheet_tab, fg_color="transparent")
    invoice_paths_section.pack(fill="x", pady=0, padx=0)
    invoice_paths_section.grid_columnconfigure(1, weight=1)

    # Invoice Sheet
    ctk.CTkLabel(invoice_paths_section, 
                 font=fonts.heading_font,
                 text="Sheet:").grid(row=0, column=0, padx=(20, 10), sticky="w")

    ctk.CTkEntry(invoice_paths_section, 
             textvariable=globals.sheet_invoices_var).grid(row=0, column=1, padx=(0, 10), sticky="ew")
    
    # Invoice Table
    ctk.CTkLabel(invoice_paths_section, 
                 font=fonts.heading_font,
                 text="Table:").grid(row=1, column=0, padx=(20, 10), sticky="w")

    ctk.CTkEntry(invoice_paths_section, 
             textvariable=globals.table_InvoiceTable_var).grid(row=1, column=1, padx=(0, 10), sticky="ew")

    # Invoice Starting Row
    ctk.CTkLabel(invoice_paths_section, 
                 font=fonts.heading_font,
                 text="First Row:").grid(row=2, column=0, padx=(20, 10), sticky="w")

    slider_frame_1 = ctk.CTkFrame(invoice_paths_section, fg_color="transparent")
    slider_frame_1.grid(row=2, column=1, padx=(0, 10), sticky="w")

    slider_1 = ctk.CTkSlider(slider_frame_1, 
             variable=globals.invoice_starting_row_var,
             from_=1, to=10, number_of_steps=9,
             width=200)
    slider_1.pack(side="left", padx=(0, 8))
    
    slider_label_1 = ctk.CTkLabel(slider_frame_1, 
                 textvariable=globals.invoice_starting_row_var)
    slider_label_1.pack(side="left")

    # Invoice Starting Column
    ctk.CTkLabel(invoice_paths_section, 
                 font=fonts.heading_font,
                 text="First Column:").grid(row=3, column=0, padx=(20, 10), sticky="w")

    slider_frame_2 = ctk.CTkFrame(invoice_paths_section, fg_color="transparent")
    slider_frame_2.grid(row=3, column=1, padx=(0, 10), sticky="w")

    slider_2 = ctk.CTkSlider(slider_frame_2, 
             variable=globals.invoice_starting_column_var,
             from_=1, to=10, number_of_steps=9,
             width=200)
    slider_2.pack(side="left", padx=(0, 8))

    slider_label_2 = ctk.CTkLabel(slider_frame_2, 
                 textvariable=globals.invoice_starting_column_var)
    slider_label_2.pack(side="left")

    # Cards
    ctk.CTkLabel(spreadsheet_tab, 
                font=fonts.title_font,
                text="Cards").pack(pady=20, fill="x", anchor="center", padx=10)

    # Cards Paths Frame
    cards_paths_section = ctk.CTkFrame(spreadsheet_tab, fg_color="transparent")
    cards_paths_section.pack(fill="x", pady=0, padx=0)
    cards_paths_section.grid_columnconfigure(1, weight=1)

    # Cards Sheet
    ctk.CTkLabel(cards_paths_section, 
                 font=fonts.heading_font,
                 text="Sheet:").grid(row=0, column=0, padx=(20, 10), sticky="w")

    ctk.CTkEntry(cards_paths_section, 
             textvariable=globals.sheet_CreditCards_var).grid(row=0, column=1, padx=(0, 10), sticky="ew")
    
    # Cards Table
    ctk.CTkLabel(cards_paths_section, 
                 font=fonts.heading_font,
                 text="Table:").grid(row=1, column=0, padx=(20, 10), sticky="w")

    ctk.CTkEntry(cards_paths_section, 
             textvariable=globals.table_CreditCards_var).grid(row=1, column=1, padx=(0, 10), sticky="ew")

    # Cards Starting Row
    ctk.CTkLabel(cards_paths_section, 
                 font=fonts.heading_font,
                 text="First Row:").grid(row=2, column=0, padx=(20, 10), sticky="w")

    slider_frame_3 = ctk.CTkFrame(cards_paths_section, fg_color="transparent")
    slider_frame_3.grid(row=2, column=1, padx=(0, 10), sticky="w")

    slider_3 = ctk.CTkSlider(slider_frame_3, 
             variable=globals.card_starting_row_var,
             from_=1, to=10, number_of_steps=9,
             width=200)
    slider_3.pack(side="left", padx=(0, 8))

    slider_label_3 = ctk.CTkLabel(slider_frame_3, 
                 textvariable=globals.card_starting_row_var)
    slider_label_3.pack(side="left")
    
    # Cards Starting Column
    ctk.CTkLabel(cards_paths_section, 
                 font=fonts.heading_font,
                 text="First Column:").grid(row=3, column=0, padx=(20, 10), sticky="w")

    slider_frame_4 = ctk.CTkFrame(cards_paths_section, fg_color="transparent")
    slider_frame_4.grid(row=3, column=1, padx=(0, 10), sticky="w")

    slider_4 = ctk.CTkSlider(slider_frame_4, 
             variable=globals.card_starting_column_var,
             from_=1, to=10, number_of_steps=9,
             width=200)
    slider_4.pack(side="left", padx=(0, 8))

    slider_label_4 = ctk.CTkLabel(slider_frame_4, 
                 textvariable=globals.card_starting_column_var)
    slider_label_4.pack(side="left")

    # Purchase Orders
    ctk.CTkLabel(spreadsheet_tab, 
                font=fonts.title_font,
                text="Purchase Orders").pack(pady=20, fill="x", anchor="center", padx=10)
    
    # PO Paths Frame
    po_paths_section = ctk.CTkFrame(spreadsheet_tab, fg_color="transparent")
    po_paths_section.pack(fill="x", pady=0, padx=0)
    po_paths_section.grid_columnconfigure(1, weight=1)

    # Purchase Orders Sheet
    ctk.CTkLabel(po_paths_section, 
                 font=fonts.heading_font,
                 text="Sheet:").grid(row=0, column=0, padx=(20, 10), sticky="w")

    ctk.CTkEntry(po_paths_section, 
             textvariable=globals.sheet_PurchaseOrders_var).grid(row=0, column=1, padx=(0, 10), sticky="ew")
    
    # Purchase Orders Table
    ctk.CTkLabel(po_paths_section, 
                 font=fonts.heading_font,
                 text="Table:").grid(row=1, column=0, padx=(20, 10), sticky="w")

    ctk.CTkEntry(po_paths_section, 
             textvariable=globals.table_PurchaseOrders_var).grid(row=1, column=1, padx=(0, 10), sticky="ew")

    # Cards Starting Row
    ctk.CTkLabel(po_paths_section, 
                 font=fonts.heading_font,
                 text="First Row:").grid(row=2, column=0, padx=(20, 10), sticky="w")

    slider_frame_5 = ctk.CTkFrame(po_paths_section, fg_color="transparent")
    slider_frame_5.grid(row=2, column=1, padx=(0, 10), sticky="w")

    slider_5 = ctk.CTkSlider(slider_frame_5, 
             variable=globals.po_starting_row_var,
             from_=1, to=10, number_of_steps=9,
             width=200)
    slider_5.pack(side="left", padx=(0, 8))

    slider_label_5 = ctk.CTkLabel(slider_frame_5, 
                 textvariable=globals.po_starting_row_var)
    slider_label_5.pack(side="left")
    
    # Cards Starting Column
    ctk.CTkLabel(po_paths_section, 
                 font=fonts.heading_font,
                 text="First Column:").grid(row=3, column=0, padx=(20, 10), sticky="w")

    slider_frame_6 = ctk.CTkFrame(po_paths_section, fg_color="transparent")
    slider_frame_6.grid(row=3, column=1, padx=(0, 10), sticky="w")

    slider_6 = ctk.CTkSlider(slider_frame_6, 
             variable=globals.po_starting_column_var,
             from_=1, to=10, number_of_steps=9,
             width=200)
    slider_6.pack(side="left", padx=(0, 8))

    slider_label_6 = ctk.CTkLabel(slider_frame_6, 
                 textvariable=globals.po_starting_column_var)
    slider_label_6.pack(side="left")

    # Save Button Frame
    save_button_frame = ctk.CTkFrame(spreadsheet_tab, fg_color="transparent")
    save_button_frame.pack(pady=10)

    ctk.CTkButton(save_button_frame, 
               text="Save Settings", 
               command=lambda: save_all_settings(globals)).pack()