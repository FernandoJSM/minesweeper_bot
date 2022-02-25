import pyautogui
import cv2
from mss import mss
import numpy as np
import os
from dataclasses import dataclass
from colorama import Fore


@dataclass
class Field:
    x_coord: int
    y_coord: int
    flagged: bool = False
    minecount: int = -1


class MineSweeperBot:
    def __init__(self, width, height, images_folder):
        self.minefield_width = width
        self.minefield_height = height
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
                if field.minecount == -1:
                    row_string += f"{Fore.RESET}-\t"
                elif field.minecount == 0:
                    row_string += f"{Fore.RESET} \t"
                else:
                    if 1 <= field.minecount <= 3:
                        row_string += f"{Fore.BLUE}{field.minecount:<1}\t"
                    elif 4 <= field.minecount <= 5:
                        row_string += f"{Fore.YELLOW}{field.minecount:<1}\t"
                    elif 6 <= field.minecount <= 8:
                        row_string += f"{Fore.RED}{field.minecount:<1}\t"
            print(row_string)

    def scan_minefield(self, first_scan=False):

        screenshot = cv2.cvtColor(
            src=np.array(self.sct.grab(monitor=self.monitor)),
            code=cv2.COLOR_RGB2GRAY,
        )

        print(f"{Fore.CYAN}Escaneando o campo minado...{Fore.CYAN}")

        if first_scan:
            result = cv2.matchTemplate(
                image=self.assets["unclicked"],
                templ=screenshot,
                method=cv2.TM_CCOEFF_NORMED,
            )
            (y_coords, x_coords) = np.where(result >= 0.8)
            print(
                f"\t{Fore.YELLOW}{len(y_coords)}{Fore.CYAN} campos encontrados{Fore.RESET}"
            )
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
                            elif asset_name == "exploded":
                                print(f"{Fore.RED} Fim do jogo :( {Fore.RESET}")
                                return "gameover"
                            elif asset_name.isdigit():
                                self.minefield[i][j].minecount = int(asset_name)

        # clone = screenshot.copy()
        # for (x, y) in zip(xCoords, yCoords):
        #     # draw the bounding box on the image
        #     cv2.rectangle(clone, (x, y), (x + 20, y + 20),
        #                   (255, 0, 0), 3)
        # cv2.imshow("Before NMS", clone)
        # cv2.waitKey(0)
        a = 1

    def click(
        self,
        row=-1,
        column=-1,
        right_button=False
    ):
        if (row == -1) and (column == -1):
            row = (
                np.random.randint(
                    low=int(self.minefield_width * 0.25),
                    high=int(self.minefield_width * 0.75),
                )
                - 1
            )
            column = (
                np.random.randint(
                    low=int(self.minefield_height * 0.25),
                    high=int(self.minefield_height * 0.75),
                )
                - 1
            )
            pyautogui.click(
                x=self.minefield[row][column].x_coord + 2,
                y=self.minefield[row][column].y_coord + 2,
            )
        else:
            pyautogui.click(
                x=self.minefield[row][column].x_coord + 2,
                y=self.minefield[row][column].y_coord + 2,
                button="right" if right_button else "left"
            )

    def coordinates_around_field(self, row, column):
        coords = list()
        for i in [-1, 0, 1]:
            for j in [-1, 0, 1]:
                if (i == 0) and (j == 0):
                    continue
                if 0 <= row + i < (self.minefield_width - 1) and 0 <= column + j < (
                    self.minefield_height - 1
                ):
                    coords.append((row + i, column + j))

        return coords

    def find_mine_fields(self):
        solved_fields = list()
        mine_fields = list()
        for i in range(self.minefield_width):
            for j in range(self.minefield_height):
                coords = self.coordinates_around_field(row=i, column=j)
                solved_counter = 0
                for field_around_coords in coords:
                    if self.minefield[field_around_coords[0]][field_around_coords[1]].minecount != -1:
                        solved_counter += 1
                if solved_counter == (len(coords) - self.minefield[i][j].minecount) and self.minefield[i][j].minecount > 0:
                    solved_fields.append((i, j))

        for field in solved_fields:
            coords = self.coordinates_around_field(row=field[0], column=field[1])
            for field_around_coords in coords:
                if self.minefield[field_around_coords[0]][field_around_coords[1]].minecount == -1:
                    mine_fields.append((field_around_coords[0], field_around_coords[1]))

        return set(solved_fields), set(mine_fields)

    def run(self):
        self.scan_minefield(first_scan=True)
        self.click()

        # scan = "running"
        # while scan != "gameover":
        self.scan_minefield()

        solved_fields, mine_fields = self.find_mine_fields()

        for field in mine_fields:
            self.click(row=field[0], column=field[1], right_button=True)
        for field in solved_fields:
            self.click(row=field[0], column=field[1])
        print(solved_fields)
        print(mine_fields)
        self.print_minefield()
        # loop nos dados
        pass


if __name__ == "__main__":
    MineSweeperBot(width=9, height=9, images_folder="./bot_assets").run()
