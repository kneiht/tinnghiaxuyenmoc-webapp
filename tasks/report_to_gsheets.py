
# importing the required libraries
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials


import pytz
import datetime
# Set the time zone to GMT+7
gmt_plus_7_tz = pytz.timezone('Etc/GMT-7')


# SETUP GOOGLE SHEETS 

def get_google_sheet_credential():
    ss_cred_path = r'./gen8-database-dd56285ab212.json' # Your path to the json credential file
    from oauth2client.service_account import ServiceAccountCredentials # import oath2client
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive'] # define the scope
    creds = ServiceAccountCredentials.from_json_keyfile_name(ss_cred_path, scope) # add credentials to the account
    gc = gspread.authorize(creds) # authorize the clientsheet
    return gc


def get_update_changes(df1, df2, id_name):
    # get colum names to define location
    column_names = df1.columns.values.tolist()
    # a list to contain changes
    changes = []

    # get changed changes and values
    merged_df = df1.merge(df2, on=id_name, how='outer', suffixes=('_original', '_update'))

    # Loop over each column in df2 and update the corresponding column in df1 if it has changed
    for column in df2.columns:
        update_column_name = column + '_update'
        original_column_name = column + '_original'
        if update_column_name in merged_df.columns:
            mask = merged_df[update_column_name].notnull() & (merged_df[update_column_name] != merged_df[original_column_name])
            updated_df = merged_df[mask]
            if not updated_df.empty:
                for index, row in updated_df.iterrows():
                    #print(f"Student ID: {row[id_name]}")
                    changes.append([id_name, index + 2, column_names.index(column) +1 , row[id_name], column, row[update_column_name], row[original_column_name]])

    # return the list
    return changes


'''

columns = ['Mã HV', 'Tên', 'Lớp chính', 'Lớp phụ', 'Giới tính', 'Ngày sinh', 
           'Trường đang học', 'Phụ huynh', 'SĐT', 'Phân loại KH', 'Ghi chú']
df1 = pd.read_csv('data_original.csv').loc[:, columns]
df2 = pd.read_csv('data_update.csv').loc[:, columns]
changes = get_update_changes(df1, df2, 'Mã HV')
print(changes)


import sys
sys.exit()

'''

def get_google_sheet(gc, worksheet_id, sheet_name):
    sheet = gc.open_by_key(worksheet_id).worksheet(sheet_name)
    return sheet


def sheet_to_df(sheet, columns='All', header_row_number=1):
    # Find all cells containing the string "example"
    cell_list = sheet.findall('example')

    # Get the rows containing the matching cells
    rows = []
    for cell in cell_list:
        row = worksheet.row_values(cell.row)
        if row not in rows:
            rows.append(row)

    # Print the matching rows
    for row in rows:
        print(row)




    # get all values in the worksheet as a list of lists
    all_values = sheet.get_all_values()
    # extract the header row and the data rows
    header = all_values[header_row_number-1] # header is in row 2
    data = all_values[header_row_number:]
    # create a dataframe with the data and the header as column names

    df = pd.DataFrame(data, columns=header)

    if columns != 'All':
        df = df.loc[:, columns]

    return df


def update_student_sheet(sheet, changes):
    fresh_update_flag = False
    for change in changes:
        id_type = change[0]
        row = change[1]
        col = change[2]
        _id = change[3]
        col_name = change[4]
        value_new = change[5]
        value_old = change[6]
        if str(value_old) == 'nan': 
            value_old = "cập nhật lần đầu"
            fresh_update_flag = True
        elif str(value_old).strip() == '':
            value_old = "x"

        sheet.update_cell(row, col, value_new.strip())
        now = datetime.datetime.now(gmt_plus_7_tz)
        date_time = now.strftime("%Y/%m/%d %H:%M:%S")
        print([id_type, _id, col_name, value_old, value_new, date_time])
        log_sheet.append_row([id_type, _id, col_name, value_old.strip(), value_new.strip(), date_time])


    if fresh_update_flag:
        # add student id
        sheet.update_cell(row, 1, _id)

        # add time
        sheet.update_cell(row, col + 1, date_time)

        # coppy down formula:
        for i in range(2,11):
            formula = sheet.cell(row - 1, col + i, value_render_option='FORMULA').value
            formula = str(formula).replace(str(row-1), str(row))
            sheet.update_cell(row, col + i, formula)







gc = get_google_sheet_credential()

# sheet to storage history
sheets_storage_id = "1ezgO5jlJ9SN1gdRE0HZxAWqcfIxvNekBlZ-Oe6JRC9o"
sheets_view_id = "1hMawpEz05t5JWXoqicqpghZdCA9f98Ym30xZ0o9XzAk"



log_sheet = get_google_sheet(gc, sheets_storage_id, 'Lịch sử thay đổi')
storage_students = get_google_sheet(gc, sheets_storage_id, 'Học sinh')
storage_tuitions = get_google_sheet(gc, sheets_storage_id, 'Học phí')
storage_attendace = get_google_sheet(gc, sheets_storage_id, 'Điểm danh')
storage_classes = get_google_sheet(gc, sheets_storage_id, 'Lớp học')
storage_standard_data = get_google_sheet(gc, sheets_storage_id, 'Tiêu chuẩn dữ liệu')

sheet_view_students = get_google_sheet(gc, sheets_view_id, 'Thông tin học sinh')
sheet_view_tuitions = get_google_sheet(gc, sheets_view_id, 'Đóng phí')
sheet_view_attendance = get_google_sheet(gc, sheets_view_id, 'Điểm danh')
sheet_view_classes = get_google_sheet(gc, sheets_view_id, 'Lớp học')
sheet_view_standard_data = get_google_sheet(gc, sheets_view_id, 'Tiêu chuẩn dữ liệu')


# FLASK APP START FROM HERE
from flask import Flask, abort
app = Flask(__name__)


@app.route('/')
def index():
    return 'GEN8 SERVER'



def get_data(info_df, search_string, sheet_to_update, first_cell):
    # Filter DataFrame to only include rows that contain the search string
    filtered_df = info_df[info_df.applymap(str).apply(lambda x: search_string.lower() in ' '.join(x).lower(), axis=1)]
    # update filter data to view
    sheet_to_update.update(first_cell, [filtered_df.columns.values.tolist()] + filtered_df.values.tolist())
    return "Tìm kiếm thông tin thành công"


@app.route('/gen8db/get-data/<sheet_name>/<search_string>')
def function():
    pass


@app.route('/gen8db/get-standard-data-info')
def get_standard_data_info():
    info_df = sheet_to_df(storage_standard_data, 'All', 1)
    search_string = ''
    get_data(info_df, search_string, sheet_view_standard_data, "A1")
    return "Tìm kiếm thông tin thành công"


@app.route('/gen8db/get-class-info')
def get_class_info():
    info_df = sheet_to_df(storage_classes, 'All', 1)
    search_string = ''
    get_data(info_df, search_string, sheet_view_classes, "A1")
    return "Tìm kiếm thông tin thành công"



@app.route('/gen8db/get-attendance-info')
def get_attendance_info():
    info_df = sheet_to_df(storage_attendace, 'All', 1)
    search_string = ''
    get_data(info_df, search_string, sheet_view_attendance, "A1")
    return "Tìm kiếm thông tin thành công"


@app.route('/gen8db/search-tuition-info')
def search_tuition_info():
    info_df = sheet_to_df(storage_tuitions, 'All', 1)
    search_string = sheet_view_students.acell('B1').value
    get_data(info_df, search_string, sheet_view_tuitions, "D2")
    return "Tìm kiếm thông tin thành công"


@app.route('/gen8db/update-tuition-info')
def update_tuition_info():
    now = datetime.datetime.now(gmt_plus_7_tz)
    date_time = now.strftime("%Y/%m/%d %H:%M:%S")
    values = sheet_view_tuitions.col_values(2)
    tuition_infos = values[2:6] + [date_time] + values[7:10] + values[12:14]
    last_tuition_row = len(storage_tuitions.col_values(1)) + 1
    print(tuition_infos)

    col = 0
    for tuition_info in tuition_infos:
        col = col + 1
        storage_tuitions.update_cell(last_tuition_row, col, tuition_info.strip())

    return "Cập nhật phí thành công"







@app.route('/gen8db/search-student-info')
def search_student_info():
    info_df = sheet_to_df(storage_students, 'All', 1)
    search_string = sheet_view_students.acell('B1').value
    get_data(info_df, search_string, sheet_view_students, "A2")
    return "Tìm kiếm thông tin thành công"



@app.route('/gen8db/update-student-info')
def update_student_info():
    columns = ['Mã HV', 'Tên', 'Lớp chính', 'Lớp phụ', 'Giới tính', 'Ngày sinh', 
           'Trường đang học', 'Phụ huynh', 'SĐT', 'Phân loại KH', 'Ghi chú']
    # getting df from storage and from view to compare
    df_original = sheet_to_df(storage_students, columns, 1)
    df_update = sheet_to_df(sheet_view_students, columns, 2)
    # compare and get changes
    changes = get_update_changes(df_original, df_update, 'Mã HV')
    # update sheet
    update_student_sheet(storage_students, changes)
    return "Cập nhật thông tin thành công"


@app.route('/<path:path>')
def get_file(path):
    print(path)
    try:
        with open(path) as f:
            return f.read()
    except FileNotFoundError:
        abort(404)





if __name__ == '__main__':
    app.run(debug=True)

 