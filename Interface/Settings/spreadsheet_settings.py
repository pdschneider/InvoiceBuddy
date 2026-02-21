# Interface/Settings/spreadsheet_settings.py
import customtkinter as ctk
from customtkinter import CTkImage
import Utils.fonts as fonts
from Utils.save_settings import save_all_settings
from Utils.load_settings import load_data_path
from PIL import Image
import logging

def create_spreadsheet_settings_tab(globals, spreadsheet_tab):
    """
    Create the Settings tab for configuring paths and advanced settings.

    Args:
        globals (globals): The global configuration object containing UI variables and settings.
    """

    # Scrollable frame to house settings
    try:
        scrollable_frame = ctk.CTkScrollableFrame(spreadsheet_tab)
        scrollable_frame.pack(fill="both", expand=True, pady=0, padx=10)
    except Exception as e:
        scrollable_frame = ctk.CTkFrame(spreadsheet_tab)
        scrollable_frame.pack(fill="both", expand=True, pady=0, padx=10)
        logging.critical(f"Could not create scrollable frame: {e}. Using regular CTkFrame instead.")

    components_list = ["Company", "Date", "Invoice #", "Card Number", ""]

    # Invoices
    globals.invoice_sheet_label = ctk.CTkLabel(scrollable_frame, 
                font=fonts.title_font,
                text=globals.sheet_invoices)
    globals.invoice_sheet_label.pack(pady=20, fill="x", anchor="center", padx=10)
    
    # Invoice Paths Frame
    invoice_paths_section = ctk.CTkFrame(scrollable_frame, fg_color="transparent")
    invoice_paths_section.pack(fill="x", pady=0, padx=0)
    invoice_paths_section.grid_columnconfigure(1, weight=1)

    # Invoice Sheet
    ctk.CTkLabel(invoice_paths_section, 
                 font=fonts.heading_font,
                 text="Sheet:").grid(row=0, column=0, padx=(20, 10), sticky="w")

    ctk.CTkEntry(invoice_paths_section, 
                 width=200,
             textvariable=globals.sheet_invoices_var).grid(row=0, column=1, padx=(0, 10), sticky="w")
    
    # Invoice Table
    ctk.CTkLabel(invoice_paths_section, 
                 font=fonts.heading_font,
                 text="Table:").grid(row=1, column=0, padx=(20, 10), sticky="w")

    ctk.CTkEntry(invoice_paths_section, 
                 width=200,
             textvariable=globals.table_InvoiceTable_var).grid(row=1, column=1, padx=(0, 10), sticky="w")

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

    ctk.CTkLabel(invoice_paths_section,
                 font=fonts.heading_font,
                 text="Column Order:").grid(row=4, column=0, padx=(20, 10), sticky="w")
    
    # Invoice Components
    invoice_components_frame = ctk.CTkFrame(invoice_paths_section, fg_color="transparent")
    invoice_components_frame.grid(row=4, column=1, padx=(5, 10), sticky="w")

    invoice_a_box = ctk.CTkComboBox(invoice_components_frame, 
                                    values=components_list,
                                    variable=globals.invoice_com_a_var)
    invoice_a_box.grid(row=1, column=1, padx=5)

    invoice_b_box = ctk.CTkComboBox(invoice_components_frame, 
                                    values=components_list,
                                    variable=globals.invoice_com_b_var)
    invoice_b_box.grid(row=1, column=2, padx=5)

    invoice_c_box = ctk.CTkComboBox(invoice_components_frame, 
                                    values=components_list,
                                    variable=globals.invoice_com_c_var)
    invoice_c_box.grid(row=1, column=3, padx=5)

    invoice_d_box = ctk.CTkComboBox(invoice_components_frame, 
                                    values=components_list,
                                    variable=globals.invoice_com_d_var)
    invoice_d_box.grid(row=1, column=4, padx=5)

    # Invoice Icon
    ctk.CTkLabel(invoice_paths_section,
                 font=fonts.heading_font,
                 text="Icon:").grid(row=5, column=0, padx=(20, 10), sticky="w")
    
    invoice_icon_button = ctk.CTkButton(invoice_paths_section,
                    text=None,
                    width=45,
                    image=globals.invoice_icon)
    invoice_icon_button.grid(row=5, column=1, padx=5, sticky="w")

    ctk.CTkLabel(invoice_paths_section,
                 font=fonts.heading_font,
                 text="Select Icon:").grid(row=6, column=0, padx=(20, 10), sticky="w")

    # Invoice image selection sub-frame
    invoice_icons_frame = ctk.CTkFrame(invoice_paths_section, fg_color="transparent")
    invoice_icons_frame.grid(row=6, column=1, padx=(0, 10), sticky="w")

    def switch_invoice_icon(current_icon):
        """Switches invoice icon to selected icon"""
        globals.invoice_icon_path = current_icon
        globals.invoice_icon = CTkImage(
        light_image=Image.open(load_data_path("config", globals.invoice_icon_path)),
        dark_image=Image.open(load_data_path("config", globals.invoice_icon_path)),
        size=(30, 30))

        invoice_icon_button.configure(image=globals.invoice_icon)

    for icon in globals.icons_list:
        new_icon = CTkImage(
            light_image=Image.open(load_data_path("config", icon)),
            dark_image=Image.open(load_data_path("config", icon)),
            size=(30, 30))
        ctk.CTkButton(invoice_icons_frame,
                    text=None,
                    width=45,
                    command=lambda current_icon=icon: switch_invoice_icon(current_icon),
                    image=new_icon).pack(side="left", padx=4, pady=4)

    # Cards
    globals.card_sheet_label = ctk.CTkLabel(scrollable_frame, 
                font=fonts.title_font,
                text=globals.sheet_CreditCards)
    globals.card_sheet_label.pack(pady=20, fill="x", anchor="center", padx=10)

    # Cards Paths Frame
    cards_paths_section = ctk.CTkFrame(scrollable_frame, fg_color="transparent")
    cards_paths_section.pack(fill="x", pady=0, padx=0)
    cards_paths_section.grid_columnconfigure(1, weight=1)

    # Cards Sheet
    ctk.CTkLabel(cards_paths_section, 
                 font=fonts.heading_font,
                 text="Sheet:").grid(row=0, column=0, padx=(20, 10), sticky="w")

    ctk.CTkEntry(cards_paths_section, 
                 width=200,
             textvariable=globals.sheet_CreditCards_var).grid(row=0, column=1, padx=(0, 10), sticky="w")
    
    # Cards Table
    ctk.CTkLabel(cards_paths_section, 
                 font=fonts.heading_font,
                 text="Table:").grid(row=1, column=0, padx=(20, 10), sticky="w")

    ctk.CTkEntry(cards_paths_section, 
                 width=200,
             textvariable=globals.table_CreditCards_var).grid(row=1, column=1, padx=(0, 10), sticky="w")

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

    ctk.CTkLabel(cards_paths_section,
                 font=fonts.heading_font,
                 text="Column Order:").grid(row=4, column=0, padx=(20, 10), sticky="w")
    
    # Card Components
    card_components_frame = ctk.CTkFrame(cards_paths_section, fg_color="transparent")
    card_components_frame.grid(row=4, column=1, padx=(5, 10), sticky="w")

    card_a_box = ctk.CTkComboBox(card_components_frame, 
                                 values=components_list,
                                 variable=globals.card_com_a_var)
    card_a_box.grid(row=1, column=1, padx=5)

    card_b_box = ctk.CTkComboBox(card_components_frame, 
                                 values=components_list,
                                 variable=globals.card_com_b_var)
    card_b_box.grid(row=1, column=2, padx=5)

    card_c_box = ctk.CTkComboBox(card_components_frame, 
                                 values=components_list,
                                 variable=globals.card_com_c_var)
    card_c_box.grid(row=1, column=3, padx=5)

    card_d_box = ctk.CTkComboBox(card_components_frame, 
                                 values=components_list,
                                 variable=globals.card_com_d_var)
    card_d_box.grid(row=1, column=4, padx=5)

    ctk.CTkLabel(cards_paths_section,
                 font=fonts.heading_font,
                 text="Icon:").grid(row=5, column=0, padx=(20, 10), sticky="w")
    
    card_icon_button = ctk.CTkButton(cards_paths_section,
                  text=None,
                  width=45,
                  image=globals.card_icon)
    card_icon_button.grid(row=5, column=1, padx=5, sticky="w")

    ctk.CTkLabel(cards_paths_section,
                 font=fonts.heading_font,
                 text="Select Icon:").grid(row=6, column=0, padx=(20, 10), sticky="w")

    def switch_card_icon(current_icon):
            """Switches invoice icon to selected icon"""
            globals.card_icon_path = current_icon
            globals.card_icon = CTkImage(
            light_image=Image.open(load_data_path("config", globals.card_icon_path)),
            dark_image=Image.open(load_data_path("config", globals.card_icon_path)),
            size=(30, 30))

            card_icon_button.configure(image=globals.card_icon)

    # Cards image selection sub-frame
    cards_icons_frame = ctk.CTkFrame(cards_paths_section, fg_color="transparent")
    cards_icons_frame.grid(row=6, column=1, padx=(0, 10), sticky="w")

    for icon in globals.icons_list:
        new_icon = CTkImage(
            light_image=Image.open(load_data_path("config", icon)),
            dark_image=Image.open(load_data_path("config", icon)),
            size=(30, 30))
        ctk.CTkButton(cards_icons_frame,
                    text=None,
                    width=45,
                    command=lambda current_icon=icon: switch_card_icon(current_icon),
                    image=new_icon).pack(side="left", padx=4, pady=4)

    # Purchase Orders
    globals.po_sheet_label = ctk.CTkLabel(scrollable_frame, 
                font=fonts.title_font,
                text=globals.sheet_PurchaseOrders)
    globals.po_sheet_label.pack(pady=20, fill="x", anchor="center", padx=10)
    
    # PO Paths Frame
    po_paths_section = ctk.CTkFrame(scrollable_frame, fg_color="transparent")
    po_paths_section.pack(fill="x", pady=0, padx=0)
    po_paths_section.grid_columnconfigure(1, weight=1)

    # Purchase Orders Sheet
    ctk.CTkLabel(po_paths_section, 
                 font=fonts.heading_font,
                 text="Sheet:").grid(row=0, column=0, padx=(20, 10), sticky="w")

    ctk.CTkEntry(po_paths_section, 
                 width=200,
             textvariable=globals.sheet_PurchaseOrders_var).grid(row=0, column=1, padx=(0, 10), sticky="w")
    
    # Purchase Orders Table
    ctk.CTkLabel(po_paths_section, 
                 font=fonts.heading_font,
                 text="Table:").grid(row=1, column=0, padx=(20, 10), sticky="w")

    ctk.CTkEntry(po_paths_section, 
                 width=200,
             textvariable=globals.table_PurchaseOrders_var).grid(row=1, column=1, padx=(0, 10), sticky="w")

    # Purchase Orders Starting Row
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
    
    # Purchase Orders Starting Column
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

    ctk.CTkLabel(po_paths_section,
                 font=fonts.heading_font,
                 text="Column Order:").grid(row=4, column=0, padx=(20, 10), sticky="w")
    
    # Purchase Orders Components
    po_components_frame = ctk.CTkFrame(po_paths_section, fg_color="transparent")
    po_components_frame.grid(row=4, column=1, padx=(5, 10), sticky="w")

    po_a_box = ctk.CTkComboBox(po_components_frame, 
                               values=components_list,
                               variable=globals.po_com_a_var)
    po_a_box.grid(row=1, column=1, padx=5)

    po_b_box = ctk.CTkComboBox(po_components_frame, 
                               values=components_list,
                               variable=globals.po_com_b_var)
    po_b_box.grid(row=1, column=2, padx=5)

    po_c_box = ctk.CTkComboBox(po_components_frame, 
                               values=components_list,
                               variable=globals.po_com_c_var)
    po_c_box.grid(row=1, column=3, padx=5)

    po_d_box = ctk.CTkComboBox(po_components_frame, 
                               values=components_list,
                               variable=globals.po_com_d_var)
    po_d_box.grid(row=1, column=4, padx=5)

    ctk.CTkLabel(po_paths_section,
                 font=fonts.heading_font,
                 text="Icon:").grid(row=5, column=0, padx=(20, 10), sticky="w")
    
    po_icon_button = ctk.CTkButton(po_paths_section,
                  text=None,
                  width=45,
                  image=globals.po_icon)
    po_icon_button.grid(row=5, column=1, padx=5, sticky="w")
    
    ctk.CTkLabel(po_paths_section,
                 font=fonts.heading_font,
                 text="Select Icon:").grid(row=6, column=0, padx=(20, 10), sticky="w")

    def switch_po_icon(current_icon):
            """Switches invoice icon to selected icon"""
            globals.po_icon_path = current_icon
            globals.po_icon = CTkImage(
            light_image=Image.open(load_data_path("config", globals.po_icon_path)),
            dark_image=Image.open(load_data_path("config", globals.po_icon_path)),
            size=(30, 30))

            po_icon_button.configure(image=globals.po_icon)

    # Purchase Orders image selection sub-frame
    po_icons_frame = ctk.CTkFrame(po_paths_section, fg_color="transparent")
    po_icons_frame.grid(row=6, column=1, padx=(0, 10), sticky="w")

    for icon in globals.icons_list:
        new_icon = CTkImage(
            light_image=Image.open(load_data_path("config", icon)),
            dark_image=Image.open(load_data_path("config", icon)),
            size=(30, 30))
        ctk.CTkButton(po_icons_frame,
                    text=None,
                    width=45,
                    command=lambda current_icon=icon: switch_po_icon(current_icon),
                    image=new_icon).pack(side="left", padx=4, pady=4)

    # Save Button Frame
    save_button_frame = ctk.CTkFrame(spreadsheet_tab, fg_color="transparent")
    save_button_frame.pack(pady=10)

    ctk.CTkButton(save_button_frame, 
               text="Save Settings", 
               command=lambda: save_all_settings(globals)).pack()
