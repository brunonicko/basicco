import os
import sys


def main():
    assert len(sys.argv) == 2
    path = os.path.join(
        os.environ["TOX_ENV_DIR"],
        "tmp",
        "README_{}.py".format(os.environ["TOX_ENV_NAME"])
    )
    if sys.argv[1] == "clean":
        os.remove(path)
        sys.exit(0)
    else:
        assert sys.argv[1] == "build"

    with open("README.rst", "r") as f:
        content = f.readlines()

    blocks = {}
    block = []
    in_block = 0
    spacing = None
    for i, line in enumerate(content):
        i += 1
        line = line.strip(os.linesep)
        if line.startswith(".. code:: python"):
            if block:
                assert in_block
                blocks[in_block] = block
                block = []
            in_block = i
            spacing = None
        elif in_block:
            stripped_line = line.lstrip(" ")
            if stripped_line.startswith(">>> ") or stripped_line.startswith("... "):
                line_spacing = len(line) - len(stripped_line)
                if spacing is None:
                    spacing = line_spacing
                else:
                    assert line_spacing == spacing, (
                        "inconsistent spacing in README.rst:{}".format(i)
                    )
                block.append(line)
            elif stripped_line and spacing:
                if line[:spacing] != " " * spacing:
                    if block:
                        blocks[in_block] = block
                        block = []
                    in_block = 0
                    spacing = None
                else:
                    block.append(line)
            elif not stripped_line:
                block.append("")
    if block:
        assert in_block
        blocks[in_block] = block

    lines = ['"""']
    for i, block in sorted(blocks.items(), key=lambda p: p[0]):
        for _ in range((i - len(lines)) - 1):
            lines.append("")
        lines.append(".. code:: python")
        lines.extend(block)
    lines.append('"""')

    with open(path, "w") as f:
        f.write("\n".join(lines))


if __name__ == "__main__":
    main()
