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

            with open(file_path, 'r') as header:
                lines = header.readlines()

                if not __verify_use_ifdef(lines):
                    continue

                path_relative = file_path.replace(path_source, "")[1:]

                comments.extend(__verify_ifdef(
                    path_relative=path_relative,
                    lines=lines,
                    file=file
                ))

                comments.extend(__verify_endif(
                    path_relative=path_relative,
                    lines=lines
                ))

    return comments


def __verify_use_ifdef(lines):
    for myLine in lines:
        if myLine.strip().startswith("#pragma"):
            return False

    return True


def __verify_is_comment_line(line):
    for start_with in ["/**", " *"]:
        if line.startswith(start_with):
            return True

    return False


def __verify_ifdef(path_relative, lines, file):
    real_line = ""
    line_ifdef = 1
    current_line = 0
    start_with = "#ifndef " + file.upper().replace(".", "_").replace("-", "").replace("_P", "PRIVATE")

    for myLine in lines:
        current_line += 1

        if myLine.strip().startswith("#ifndef"):
            real_line = myLine.replace("\n", "")
            line_ifdef = current_line
            break

    comments = []

    if real_line != start_with:
        comments.append(__create_comment(
            path_relative=path_relative,
            line_number=line_ifdef,
            comment=f"Nome do ifdef nao corresponde ao nome do arquivo, no arquivo {path_relative}"
        ))

    return comments


def __verify_endif(path_relative, lines):
    found = False
    has_next_line = False
    endif_line = len(lines)
    start_with = "#endif"

    for myLine in list(reversed(lines)):
        if myLine.strip().startswith(start_with):
            found = True
            break

        if len(myLine.strip()) > 0 and not __verify_is_comment_line(myLine):
            has_next_line = True

        endif_line -= 1

    comments = []

    if not found:
        comments.append(__create_comment(
            path_relative=path_relative,
            line_number=len(lines),
            comment=f"Não existe o #endif, no arquivo {path_relative}"
        ))

    elif has_next_line:
        comments.append(__create_comment(
            path_relative=path_relative,
            line_number=endif_line,
            comment=f"Tem código abaixo do #endif, isso não é permitido, verifique no arquivo {path_relative}"
        ))

    return comments


def __create_comment(path_relative, line_number, comment):
    return {
        "id": __generate_md5(comment),
        "comment": comment,
        "position": {
            "language": "c++",
            "path": path_relative,
            "startInLine": line_number,
            "endInLine": line_number
        }
    }


def __generate_md5(string):
    md5_hash = hashlib.md5()
    md5_hash.update(string.encode('utf-8'))

    return md5_hash.hexdigest()
