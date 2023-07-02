import hashlib
import os


def review(config):
    path_source = config['path_source']
    comments = []

    for root, dirs, files in os.walk(path_source):
        for file in files:
            if not file.endswith(".h"):
                continue

            file_path = os.path.join(root, file)
            start_with = "#ifndef " + file.upper().replace(".", "_").replace("-", "").replace("_P", "PRIVATE")

            with open(file_path, 'r') as header:
                lines = header.readlines()
                real_line = ""
                line_ifdef = 1
                current_line = 0
                use_ifdef = True

                for myLine in lines:
                    current_line += 1

                    if myLine.strip().startswith("#ifndef"):
                        real_line = myLine.replace("\n", "")
                        line_ifdef = current_line
                        break

                    if myLine.strip().startswith("#pragma"):
                        use_ifdef = False
                        break

                if use_ifdef and real_line != start_with:
                    path_relative = file_path.replace(path_source, "")[1:]
                    comments.append({
                        "id": __generate_md5(file_path),
                        "comment": f"Nome do ifdef nao corresponde ao nome do arquivo, no arquivo {path_relative}",
                        "position": {
                            "language": "c++",
                            "path": path_relative,
                            "startInLine": line_ifdef,
                            "endInLine": line_ifdef
                        }
                    })

    return comments


def __generate_md5(string):
    md5_hash = hashlib.md5()
    md5_hash.update(string.encode('utf-8'))

    return md5_hash.hexdigest()
