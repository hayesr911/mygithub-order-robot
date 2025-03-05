from robocorp.tasks import task
from robocorp import browser
from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive
from RPA.FileSystem import FileSystem
@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    open_robot_order_website()
    close_annoying_modal()
    download_cvs_data_file()
    fill_form_with_cvs_data()
    archive_receipts()


def open_robot_order_website():
    """
    Navigate to RobotSpareBin website
    """
    browser.goto("https://robotsparebinindustries.com/#/robot-order")

def download_cvs_data_file():
    http = HTTP()
    http.download("https://robotsparebinindustries.com/orders.csv", overwrite=True)

def fill_form_with_cvs_data():
    """
    Read data from cvs and fill in the order form
    """
    tables = Tables()
    data = tables.read_table_from_csv("orders.csv")
    for row in data:
        #print(row)
        get_order(row)

def close_annoying_modal():
    page = browser.page()
    page.click("//button[text()='OK']")

def get_order(order_item):

    """
    Get orders from csv data
    """
    page = browser.page()
    page.select_option("#head", str(order_item["Head"]))
    page.check("//input[@id='id-body-1']")
    #page.check()
    page.fill("//input[@type='number']", str(order_item["Legs"]))
    page.fill("#address", str(order_item["Address"]))
    page.click("//button[text()='Order']")
    try:
        page.wait_for_selector("//*[@id='receipt']")
    except Exception:
        page.click("//button[text()='Order']")
        page.wait_for_selector("//*[@id='receipt']")
    order_number = page.locator("//p[@class='badge badge-success']").inner_text()
    receipt = page.locator("//*[@id='receipt']").inner_html()
    pdf_file = store_receipt_as_pdf(receipt, order_number)
    screenshot = screenshot_robot(order_number)
    embed_screenshot_to_receipt(screenshot, pdf_file)
    page.click("//button[text()='Order another robot']")
    page.click("//button[text()='OK']")

def store_receipt_as_pdf(receipt, order_number):
    """
    """
   
    pdf = PDF()
    pdf.html_to_pdf(receipt, f"output/{order_number}.pdf")
    pdf_file =f"output/{order_number}.pdf"
    return pdf_file
    
   
def screenshot_robot(order_number):
    """
    """
    page = browser.page()
    page.screenshot(path=f"output/{order_number}.png")
    screenshot =f"output/{order_number}.png"
    return screenshot
     
def embed_screenshot_to_receipt(screenshot, pdf_file):
    """
    """
    pdf = PDF()
    pdf.open_pdf(pdf_file)
    pdf.add_watermark_image_to_pdf(image_path=screenshot,
                                output_path=pdf_file)
    pdf.save_pdf(output_path=pdf_file)


def archive_receipts():
    """
    Create Archive of receipt anf screenshor of the robot orders
    """
    lib = FileSystem()
    lib.create_directory("output/archive")

    matches = lib.find_files("output/*.pdf")
    if matches:
        lib.move_files(matches, "output/archive")
    
    matches = lib.find_files("output/*.png")
    if matches:
        lib.move_files(matches, "output/archive")
    lib = Archive()
    lib.archive_folder_with_zip('./output/archive', 'mydocs.zip')
    