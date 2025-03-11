import os
import numpy as np
import pandas as pd
import re
import calendar
from openpyxl import Workbook
from openpyxl.styles import PatternFill
from openpyxl.utils.dataframe import dataframe_to_rows

def load_absensi(file_path):
    """Membaca file Excel absensi."""
    try:
        data = pd.read_excel(file_path, sheet_name="Catatan Kehadiran Karyawan")
        return data
    except Exception as e:
        print(f"❌ Error loading file: {e}")
        return None

def extract_employee_data(data):
    """Menentukan indeks ID, Nama, dan Waktu dari data absensi."""
    user_id_rows = data[data.iloc[:, 4] == "User ID.："].index
    return user_id_rows

def process_time_data(data, user_id_rows):
    """Membuat DataFrame dengan format ID, Nama, Jenis, dan data waktu absen harian."""
    columns = ["ID", "Nama", "Jenis"] + [str(day) for day in range(1, 32)]
    extended_attendance_df = pd.DataFrame(columns=columns)

    for user_row in user_id_rows:
        user_id = data.iloc[user_row, 5]
        user_name = data.iloc[user_row, 11]
        
        user_dict_datang = {'ID': user_id, 'Nama': user_name, 'Jenis': 'Datang', **{str(day): None for day in range(1, 32)}}
        user_dict_pulang = {'ID': user_id, 'Nama': user_name, 'Jenis': 'Pulang', **{str(day): None for day in range(1, 32)}}

        current_row = user_row + 2
        while current_row < len(data):
            time_data = data.iloc[current_row, 1:32].values  
            valid_times_per_day = {}

            for i, entry in enumerate(time_data):
                day = str(i + 1)
                if pd.notna(entry):
                    entry = str(entry)
                    entries = entry.split('\n')
                    times = sorted([time.strip() for time in entries if re.match(r'^\d{2}:\d{2}$', time.strip())])

                    if times:
                        valid_times_per_day[day] = times
            
            if valid_times_per_day:
                for day, times in valid_times_per_day.items():
                    datang_time = None
                    pulang_time = None

                    # Jika hanya ada satu waktu, tentukan berdasarkan jam
                    if len(times) == 1:
                        hour = int(times[0].split(":")[0])
                        if hour < 13:
                            datang_time = times[0]
                        else:
                            pulang_time = times[0]
                    else:
                        # Jika lebih dari satu waktu
                        datang_candidates = [t for t in times if int(t.split(":")[0]) < 13]
                        pulang_candidates = [t for t in times if int(t.split(":")[0]) >= 13]

                        if datang_candidates:
                            datang_time = datang_candidates[0]
                        if pulang_candidates:
                            pulang_time = pulang_candidates[-1]

                    user_dict_datang[day] = datang_time if datang_time else None
                    user_dict_pulang[day] = pulang_time if pulang_time else None
            
            else:
                break

            current_row += 1

        extended_attendance_df = pd.concat([
            extended_attendance_df,
            pd.DataFrame([user_dict_datang]),
            pd.DataFrame([user_dict_pulang])
        ], ignore_index=True)

    return extended_attendance_df

def expand_rows_based_on_semicolon(df):
    """Memisahkan data dengan banyak waktu menjadi baris yang terpisah"""
    new_rows = []
    for _, row in df.iterrows():
        base_data = row.to_dict()
        max_splits = 1  

        for col in df.columns:
            if isinstance(row[col], str) and ';' in row[col]:
                split_count = len(row[col].split(';'))
                max_splits = max(max_splits, split_count)
        
        for i in range(max_splits):
            new_row = base_data.copy()
            for col in df.columns:
                if isinstance(row[col], str) and ';' in row[col]:
                    split_parts = row[col].split(';')
                    if i < len(split_parts):
                        new_row[col] = split_parts[i]
                    else:
                        new_row[col] = None
            new_rows.append(new_row)

    expanded_df = pd.DataFrame(new_rows)
    return expanded_df

def save_preprocessed_data(df, filename="processed_absensi.xlsx"):
    """Menyimpan DataFrame hasil preprocessing ke file Excel."""
    save_dir = "media"
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    save_path = os.path.join(save_dir, filename)
    df.to_excel(save_path, index=False)
    return save_path

def preprocess_absensi(file_path):
    """Fungsi utama untuk menjalankan preprocessing absensi."""
    print(f"📂 Processing file: {file_path}")

    data = load_absensi(file_path)
    if data is None:
        return None
    
    user_id_rows = extract_employee_data(data)
    if user_id_rows.empty:
        print("⚠️ Tidak ada data ID karyawan yang ditemukan.")
        return None

    attendance_df = process_time_data(data, user_id_rows)
    expanded_df = expand_rows_based_on_semicolon(attendance_df)
    file_path = save_preprocessed_data(expanded_df)

    return {"processed_data": expanded_df, "file_path": file_path}

if __name__ == "__main__":
    file_path = r"C:\\Magang CESGS\\cesgs_web_hr\\1_(Mei)Catatan Kehadiran Karyawan.xls"
    result = preprocess_absensi(file_path)
    if result:
        print("\n✅ Data Absensi yang Diproses:")
        print(result['processed_data'].head())
