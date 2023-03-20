from mytoolbox.MyPyInstaller import MyPyInstaller

if __name__ == "__main__":
    pi = MyPyInstaller(gui_app=False,
                       one_file=True,
                       exe_file_name="Google FIT steps generator",
                       icon_path="images\\ico.ico",
                       included_folder_path="gFIT",
                       # py_file_name="Examples\\file_test.py"
                       )
