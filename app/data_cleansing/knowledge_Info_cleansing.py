import sys

from app.services.knowledge_base_service import (insert_major_library01_data, insert_major_library02_data,
                                                 insert_major_library03_data, insert_major_library04_data,
                                                 insert_major_library05_data, insert_major_library06_data,
                                                 clear_all_data)

if __name__ == '__main__':
    print('参数错误')
    #     根据命令行参数 insert_major_library01_data 选择执行不同的操作，可以数数组类型进行多个操作
    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            if arg == 'insert_major_library01_data':
                insert_major_library01_data()
            elif arg == 'insert_major_library02_data':
                insert_major_library02_data()
            elif arg == 'insert_major_library03_data':
                insert_major_library03_data()
            elif arg == 'insert_major_library04_data':
                insert_major_library04_data()
            elif arg == 'insert_major_library05_data':
                insert_major_library05_data()
            elif arg == 'insert_major_library06_data':
                insert_major_library06_data()
            elif arg == 'clear_all_data':
                id = sys.argv[2]
                database = f"zn_school_department_project_{id}"
                clear_all_data(database)

    else:
        print('参数错误')
        sys.exit(1)
