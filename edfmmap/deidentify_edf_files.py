from edfheader import *

if __name__ == "__main__":
    from pathlib import Path
    import shutil

    file_list = glob.glob("*.edf")
    print(file_list)

    # copystat so that files auto-sort
    # for fn in file_list:
    #     eeg_rptkey = fn[:-9]

    #     eeg_path = Path(eeg_rptkey + ".eeg")
    #     print(eeg_rptkey, str(eeg_path), eeg_path.exists())
    #     shutil.copystat(eeg_path, fn)
    #     backpath = Path(fn + ".backup")
    #     shutil.copystat(eeg_path, backpath)
    # make backups if they don't exist
    for fn in file_list:
        fpath = Path(fn)
        backpath = Path(fn + ".backup")
        if backpath.exists():
            print(f"backup already exists for {fpath}")
        else:
            shutil.copy2(fpath, backpath)
            # shutil.copystat(fpath, backpath)
    for fn in file_list:
        eh = EdfHeader(fn)
        if Path(fn + ".hdr").exists():
            print("header already written")
        else:
            eh.save_header()
        eh.deindentify()
