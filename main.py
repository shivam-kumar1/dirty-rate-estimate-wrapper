import os
from shutil import make_archive

FIELD_HOST_IP = "Host IP"
FIELD_VM_UUID = "VM UUID"
FIELD_DIRTY_RATE = "Dirty Rate"
FIELD_IS_MIGRATABLE = "Is Migratable?"
FIELD_IS_BORDERLINE = "Is Borderline?"

STR_AVG_DIRTY_RATE = "Average absolute dirty rate"
STR_MIGRATABLE = "VM is expected to migrate"
STR_NOT_MIGRATABLE = "VM is not expected to migrate"
STR_BORDERLINE = "Dirty Rate of VM is close to threshold"

LOG_FOLDER = "analysis"
MIGRATABILITY_REPORT = "migratability_report.csv"
LOG_ARCHIVE = "dirty_rate_estimate"

def analyse():
    curr_dir = os.getcwd()
    out_file_path = "{}/{}".format(curr_dir, MIGRATABILITY_REPORT)
    log_files_path = "{}/{}".format(curr_dir, LOG_FOLDER)

    make_archive(LOG_ARCHIVE, "zip", LOG_FOLDER)

    out_file = open(out_file_path, "w")
    out_file.write("{},{},{},{},{}\n"
                    .format(FIELD_HOST_IP, FIELD_VM_UUID, FIELD_DIRTY_RATE,
                            FIELD_IS_MIGRATABLE, FIELD_IS_BORDERLINE))

    for file in os.listdir(log_files_path):
        log_file_path = "{}/{}".format(log_files_path, file)
        log_file = open(log_file_path, "r")
        logs = log_file.readlines()
        len_logs = len(logs)

        host_ip = file.split("_")[2]
        vm_uuid = ""
        dirty_rate = None
        migratable = None
        borderline = None

        for i in range(len_logs):
            line = logs[i]

            if STR_AVG_DIRTY_RATE in line:
                vm_uuid = line.split("[")[1][:36]
                dirty_rate = line.split(" ")[-2]

            if STR_MIGRATABLE in line:
                if vm_uuid != line.split("[")[1][:36] or dirty_rate is None:
                    raise Exception("Missing data!")

                migratable = True
                if i + 1 < len_logs and STR_BORDERLINE in logs[i + 1]:
                    borderline = True
                else:
                    borderline = False

                out_file.write("{},{},{},{},{}\n"
                        .format(host_ip, vm_uuid, dirty_rate, migratable,
                                borderline))

            if STR_NOT_MIGRATABLE in line:
                if vm_uuid != line.split("[")[1][:36] or dirty_rate is None:
                    raise Exception("Missing data!")

                migratable = False
                if i + 1 < len_logs and STR_BORDERLINE in logs[i + 1]:
                    borderline = True
                else:
                    borderline = False

                out_file.write("{},{},{},{},{}\n"
                        .format(host_ip, vm_uuid, dirty_rate, migratable,
                                borderline))

if __name__ == "__main__":
    analyse()

