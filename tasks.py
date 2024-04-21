# from robocorp.tasks import task
# from robocorp import browser

# from RPA.HTTP import HTTP
# from RPA.Tables import Tables
# from RPA.Browser.Selenium import Selenium
# from RPA.PDF import PDF
# from RPA.Archive import Archive
# import shutil

# @task
# def order_robot_from_RobotSpareBin():
#     """
#     Orders robots from RobotSpareBin Industries Inc.
#     Saves the order HTML receipt as a PDF file.
#     Saves the screenshot of the ordered robot.
#     Embeds the screenshot of the robot to the PDF receipt.
#     Creates ZIP archive of the receipts and the images.
#     """ 
#     browser.configure(
#         slowmo=500
#     )
#     orders = download_order_file()

#     open_robot_order_website()
#     close_annoying_modal()

#     for order in orders:
#         fill_and_submit_data(order)
#         screenshot_order()
#         store_receipt_pdf(order["Order number"])
#         close_annoying_modal()
    
#     archive_receipts()
#     clean_up()


# def open_robot_order_website() -> None:
#     browser.goto("https://robotsparebinindustries.com/#/robot-order")
#     page = browser.page()
#     page.click("text=OK")

# def download_order_file() -> list:
#     http = HTTP()
#     http.download("https://robotsparebinindustries.com/orders.csv", overwrite=True)

# def order_another_robot():
#     browser.goto("https://robotsparebinindustries.com/#/robot-order")
#     page = browser.page()
#     page.click("text=OK")

# def process_order():
#     download_order_file()
#     tables = Tables()
#     orders_table = tables.read_table_from_csv("orders.csv", )
    
#     for row in orders_table:
#         print(row)

#     return orders_table

# def close_annoying_modal() -> None:
#     # browser.click_button("//*[@id='root']/div/div[2]/div/div/div/div/div/button[1]")
#     page = browser.page()
#     page.click("button:text('OK')")

# def fill_and_submit_data(order):
#     page = browser.page()
#     head_names = {
#         "1": "Roll-a-thor head",
#         "2": "Peanut crusher head",
#         "3": "D.A.V.E head",
#         "4": "Andy Roid head",
#         "5": "Spanner mate head",
#         "6": "Drillbit 200 head"
#     }
#     head_number = order["Head"]
#     page.select_option("#head", head_names.get(head_number))
#     page.click('//*[@id="root"]/div/div[1]/div/div[1]/form/div[2]/div/div[{0}]/label'.format(order["Body"]))
#     page.fill("input[placeholder='Enter the part number for the legs']", order["Legs"])
#     page.fill("#address", order["Address"])
#     while True:
#         page.click("#order")
#         order_another = page.query_selector("#order-another")
#         if order_another:
#             pdf_path = store_receipt_pdf(int(order["Order number"]))
#             screenshot_path = screenshot_order(int(order["Order number"]))
#             embed_screenshot_to_receipt(screenshot_path, pdf_path)
#             order_another_robot()
#             close_annoying_modal()
#             break


# def store_receipt_pdf(order_number):
#     page = browser.page()
#     order_receipt_html = page.locator("#receipt").inner_html()
#     pdf = PDF()
#     pdf_path = "output/receipts/{0}.pdf".format(order_number)
#     pdf.html_to_pdf(order_receipt_html, pdf_path)
#     return pdf_path

# def screenshot_order(order_number):
#     page = browser.page()
#     screenshot_path = "output/screenshots/{0}.png".format(order_number)
#     page.locator("#robot-preview-image").screenshot(path=screenshot_path)
#     return screenshot_path

# def embed_screenshot_to_receipt(screenshot_path, pdf_path):
#     pdf = PDF()
#     pdf.add_watermark_image_to_pdf(image_path=screenshot_path, 
#                                    source_path=pdf_path, 
#                                    output_path=pdf_path)
    
# def fill_form_with_csv_data():
#     csv_file = Tables()
#     robot_orders = csv_file.read_table_from_csv("orders.csv")
#     for order in robot_orders:
#         fill_and_submit_data(order)

# def archive_receipts():
#     """Archives all the receipt pdfs into a single zip archive"""
#     lib = Archive()
#     lib.archive_folder_with_zip("./output/receipts", "./output/receipts.zip")

# def clean_up():
#     """Cleans up the folders where receipts and screenshots are saved."""
#     shutil.rmtree("./output/receipts")
#     shutil.rmtree("./output/screenshots")


import os
from robocorp.tasks import task
from robocorp import browser

from RPA.HTTP import HTTP
from RPA.PDF import PDF
from RPA.Tables import Tables
from RPA.Archive import Archive


@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    browser.configure(
        slowmo = 200
    )
    orders = get_orders()

    open_robot_order_website()
    close_annoying_modal()

    for order in orders:
        fill_the_form(order)
        screenshot_robot()
        store_receipt_as_pdf(order["Order number"])
        order_another()
        close_annoying_modal()

    archive_receipts()


def open_robot_order_website():
    browser.goto("https://robotsparebinindustries.com/#/robot-order")


def close_annoying_modal():
    page = browser.page()
    page.click('text=OK')


def get_orders():
    http = HTTP()
    http.download(url="https://robotsparebinindustries.com/orders.csv", overwrite=True)

    library = Tables()
    orders = library.read_table_from_csv("orders.csv")

    return orders


def fill_the_form(order):
    page = browser.page()
    page.select_option("#head", str(order["Head"]))
    page.click(f"#id-body-{order['Body']}")
    page.fill(
        '//input[@placeholder="Enter the part number for the legs"]', str(order["Legs"])
    )
    page.fill("#address", str(order["Address"]))

    page.click("button:text('Order')")
    while page.locator("//div[@class='alert alert-danger']").is_visible():
        page.click("button:text('Order')")


def store_receipt_as_pdf(order_number):
    page = browser.page()
    receipt = page.locator("#receipt").inner_html()

    pdf = PDF()
    receipt_pdf_path = f"output/receipts/receipt-{order_number}.pdf"
    pdf.html_to_pdf(receipt, receipt_pdf_path)

    pdf.add_watermark_image_to_pdf(
        image_path="output/robot.png",
        source_path=receipt_pdf_path,
        output_path=receipt_pdf_path,
    )

    os.remove("output/robot.png")


def screenshot_robot():
    page = browser.page()
    locator = page.locator("#robot-preview-image")
    screenshot = browser.screenshot(locator)

    with open("output/robot.png", "wb") as image_file:
        image_file.write(screenshot)


def order_another():
    page = browser.page()
    page.click("button:text('Order another robot')")


def archive_receipts():
    lib = Archive()
    lib.archive_folder_with_zip("output/receipts", "output/receipts.zip")







