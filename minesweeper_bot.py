import pyautogui
import cv2
from mss import mss
import numpy as np
import os
from dataclasses import dataclass
from colorama import Fore, init

init()


@dataclass
class Field:
    x_coord: int
    y_coord: int
    clicked: bool = False
    solved: bool = False
    minecount: int = -1
    mine_probability: float = -1


class MineSweeperBot:
    def __init__(self, width, height, minecount, images_folder):
        self.minefield_width = width
        self.minefield_height = height
        self.minecount = minecount
        self.images_folder = images_folder

        self.monitor = {"top": 0, "left": 0, "width": 1366, "height": 768}
        self.sct = mss()

        self.minefield = list()

        self.assets = {
            "unclicked": cv2.cvtColor(
                src=cv2.imread(os.path.join(self.images_folder, "unclicked.png")),
                code=cv2.COLOR_RGB2GRAY,
            ),
            "blank": cv2.cvtColor(
                src=cv2.imread(os.path.join(self.images_folder, "blank.png")),
                code=cv2.COLOR_RGB2GRAY,
            ),
            "exploded": cv2.cvtColor(
                src=cv2.imread(os.path.join(self.images_folder, "exploded_mine.png")),
                code=cv2.COLOR_RGB2GRAY,
            ),
            "1": cv2.cvtColor(
                src=cv2.imread(os.path.join(self.images_folder, "1.png")),
                code=cv2.COLOR_RGB2GRAY,
            ),
            "2": cv2.cvtColor(
                src=cv2.imread(os.path.join(self.images_folder, "2.png")),
                code=cv2.COLOR_RGB2GRAY,
            ),
            "3": cv2.cvtColor(
                src=cv2.imread(os.path.join(self.images_folder, "3.png")),
                code=cv2.COLOR_RGB2GRAY,
            ),
            "4": cv2.cvtColor(
                src=cv2.imread(os.path.join(self.images_folder, "4.png")),
                code=cv2.COLOR_RGB2GRAY,
            ),
            "5": cv2.cvtColor(
                src=cv2.imread(os.path.join(self.images_folder, "5.png")),
                code=cv2.COLOR_RGB2GRAY,
            ),
            "6": cv2.cvtColor(
                src=cv2.imread(os.path.join(self.images_folder, "6.png")),
                code=cv2.COLOR_RGB2GRAY,
            ),
            "7": cv2.cvtColor(
                src=cv2.imread(os.path.join(self.images_folder, "7.png")),
                code=cv2.COLOR_RGB2GRAY,
            ),
            "8": cv2.cvtColor(
                src=cv2.imread(os.path.join(self.images_folder, "8.png")),
                code=cv2.COLOR_RGB2GRAY,
            ),
        }
        self.field_shape = self.assets["unclicked"].shape

    def print_minefield(self):
        for i in range(self.minefield_width):
            row_string = ""
            for j in range(self.minefield_height):
                field = self.minefield[i][j]
                if field.mine_probability == 1:
                    row_string += f"{Fore.RED}*\t"
                elif field.solved:
                    row_string += f"{Fore.RESET}{field.minecount:<1}\t"
                elif field.minecount == -1:
                    row_string += f"{Fore.RESET}-\t"
                elif field.minecount == 0:
                    row_string += f"{Fore.RESET} \t"
                elif 1 <= field.minecount <= 2:
                    row_string += f"{Fore.BLUE}{field.minecount:<1}\t"
                elif 3 <= field.minecount <= 5:
                    row_string += f"{Fore.YELLOW}{field.minecount:<1}\t"
                elif 6 <= field.minecount <= 8:
                    row_string += f"{Fore.MAGENTA}{field.minecount:<1}\t"
            print(row_string)

    def scan_minefield(self, first_scan=False):

        screenshot = cv2.cvtColor(
            src=np.array(self.sct.grab(monitor=self.monitor)),
            code=cv2.COLOR_RGB2GRAY,
        )

        if first_scan:
            result = cv2.matchTemplate(
                image=self.assets["unclicked"],
                templ=screenshot,
                method=cv2.TM_CCOEFF_NORMED,
            )
            (y_coords, x_coords) = np.where(result >= 0.8)
            counter = 0

            for i in range(self.minefield_width):
                self.minefield.append(list())
                for j in range(self.minefield_height):
                    self.minefield[i].append(
                        Field(x_coord=x_coords[counter], y_coord=y_coords[counter])
                    )
                    counter += 1
        else:
            for i in range(self.minefield_width):
                for j in range(self.minefield_height):
                    roi = screenshot[
                        self.minefield[i][j].y_coord : self.minefield[i][j].y_coord
                        + self.field_shape[0],
                        self.minefield[i][j].x_coord : self.minefield[i][j].x_coord
                        + self.field_shape[1],
                    ]
                    a = 1
                    for asset_name, asset_image in self.assets.items():
                        result = cv2.matchTemplate(
                            image=asset_image,
                            templ=roi,
                            method=cv2.TM_CCOEFF_NORMED,
                        )
                        if np.where(result >= 0.9)[0].size:
                            if asset_name == "blank":
                                self.minefield[i][j].minecount = 0
                                self.minefield[i][j].mine_probability = 0
                            elif asset_name == "exploded":
                                self.minefield[i][j].mine_probability = 1
                                return "gameover"
                            elif asset_name.isdigit():
                                self.minefield[i][j].minecount = int(asset_name)
                                self.minefield[i][j].mine_probability = 0

    def click(self, row=-1, column=-1, random_field=False, button="left"):
        if random_field:
            unclicked_fields = list()
            for i in range(self.minefield_width):
                for j in range(self.minefield_height):
                    if self.minefield[i][j].minecount == -1 and self.minefield[i][j].mine_probability != 1:
                        unclicked_fields.append((i, j))
            random_field = unclicked_fields[np.random.randint(len(unclicked_fields))]
            row = random_field[0]
            column = random_field[1]

        pyautogui.click(
            x=self.minefield[row][column].x_coord + self.field_shape[0] // 2,
            y=self.minefield[row][column].y_coord + self.field_shape[1] // 2,
            button=button,
        )
        self.minefield[row][column].clicked = True

    def coordinates_around_field(self, row, column):
        coords = list()
        for i in [-1, 0, 1]:
            for j in [-1, 0, 1]:
                if (i == 0) and (j == 0):
                    continue
                if (
                    0 <= row + i < self.minefield_width
                    and 0 <= column + j < self.minefield_height
                ):
                    coords.append((row + i, column + j))

        return coords

    def find_mine_fields(self):
        solved_fields = list()
        mine_fields = list()
        for i in range(self.minefield_width):
            for j in range(self.minefield_height):
                if self.minefield[i][j].solved:
                    continue
                coords = self.coordinates_around_field(row=i, column=j)
                solved_counter = 0
                for field_around_coords in coords:
                    if (
                        self.minefield[field_around_coords[0]][
                            field_around_coords[1]
                        ].minecount
                        != -1
                    ):
                        solved_counter += 1
                if (
                    solved_counter == (len(coords) - self.minefield[i][j].minecount)
                ) and self.minefield[i][j].minecount > 0:
                    self.minefield[i][j].solved = True
                    solved_fields.append((i, j))

        for field in solved_fields:
            coords = self.coordinates_around_field(row=field[0], column=field[1])
            for field_around_coords in coords:
                if (
                    self.minefield[field_around_coords[0]][
                        field_around_coords[1]
                    ].mine_probability
                    == -1
                ):
                    mine_fields.append((field_around_coords[0], field_around_coords[1]))

        return set(mine_fields)

    def find_solved_fields(self):
        solved_fields = list()
        for i in range(self.minefield_width):
            for j in range(self.minefield_height):
                if self.minefield[i][j].solved:
                    continue
                coords = self.coordinates_around_field(row=i, column=j)
                mine_counter = 0
                for field_around_coords in coords:
                    if (
                        self.minefield[field_around_coords[0]][
                            field_around_coords[1]
                        ].mine_probability
                        == 1
                    ):
                        mine_counter += 1
                if (mine_counter == self.minefield[i][j].minecount) and self.minefield[
                    i
                ][j].minecount > 0:
                    solved_fields.append((i, j))
        return solved_fields

    def run(self):
        self.scan_minefield(first_scan=True)
        field_count = len(self.minefield) * len(self.minefield[0])
        print(
            f"{Fore.RESET}0 - {Fore.CYAN}Escaneando campo minado: {Fore.YELLOW}{field_count}{Fore.CYAN} campos encontrados"
        )
        self.click(random_field=True)

        iteration = 0
        minecount = 0

        while True:
            iteration += 1
            scan = self.scan_minefield()
            if scan == "gameover":
                print(f"{Fore.RESET}{iteration} - {Fore.RED}Fim do jogo :(")
                break

            mine_fields = self.find_mine_fields()

            if len(mine_fields):
                print(
                    f"{Fore.RESET}{iteration} - {Fore.CYAN}Marcando {Fore.YELLOW}{len(mine_fields)}{Fore.CYAN} campos com minas"
                )
                for field in mine_fields:
                    self.click(row=field[0], column=field[1], button="right")
                    self.minefield[field[0]][field[1]].mine_probability = 1
                    self.minefield[field[0]][field[1]].solved = True
                    minecount += 1

            solved_fields = self.find_solved_fields()

            for field in solved_fields:
                if self.minefield[field[0]][field[1]].solved:
                    continue
                self.click(row=field[0], column=field[1], button="middle")
                self.minefield[field[0]][field[1]].solved = True

            if minecount == self.minecount:
                print(f"{Fore.RESET}{iteration} - {Fore.BLUE}Fim do jogo!")
                break

            if len(mine_fields) == 0:
                print(
                    f"{Fore.RESET}{iteration} - {Fore.CYAN}Nenhuma ação possível, {Fore.YELLOW}clicando em um campo aleatório"
                )
                self.click(random_field=True)

        self.print_minefield()


if __name__ == "__main__":
    easy = {"width": 9, "height": 9, "minecount": 9}
    medium = {"width": 16, "height": 16, "minecount": 40}
    expert = {"width": 30, "height": 16, "minecount": 99}
    MineSweeperBot(
        width=medium["width"],
        height=medium["height"],
        minecount=medium["minecount"],
        images_folder="./bot_assets",
    ).run()
