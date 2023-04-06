import pygame
import sys
import tkinter as tk
from tkinter import messagebox

BOARD_SIZE = 3
SQUARE_SIZE = 200
LINE_WIDTH = 8
MARGIN = 100
TEXT_MARGIN = 50
WINDOW_SIZE = BOARD_SIZE * SQUARE_SIZE + 2 * MARGIN
TEXT_AREA_HEIGHT = 140
BOARD = [['-' for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
WIDTH = 100
HEIGHT = 100

pygame.init()

DISCORD_GRAY = (54, 57, 63)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GRAY = (200, 200, 200)
BLACK = (0, 0, 0)

pygame.font.init()
myfont = pygame.font.SysFont('Comic Sans MS', 60)

pygame.display.set_caption("Three Men's Morris")
screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE + TEXT_AREA_HEIGHT))

def draw_board():
    for i in range(1, BOARD_SIZE):
        pygame.draw.line(screen, GRAY, (MARGIN + i * SQUARE_SIZE, MARGIN), (MARGIN + i * SQUARE_SIZE, WINDOW_SIZE - MARGIN), LINE_WIDTH)
        pygame.draw.line(screen, GRAY, (MARGIN, MARGIN + i * SQUARE_SIZE), (WINDOW_SIZE - MARGIN, MARGIN + i * SQUARE_SIZE), LINE_WIDTH)
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            draw_piece(row, col, BOARD[row][col])

def draw_piece(row, col, player, is_selected=False):
    if player != '-':
        position = (MARGIN + col * SQUARE_SIZE + SQUARE_SIZE // 2, MARGIN + row * SQUARE_SIZE + SQUARE_SIZE // 2)
        if player == 'X':
            pygame.draw.circle(screen, RED, position, SQUARE_SIZE // 4)
        else:
            pygame.draw.circle(screen, BLUE, position, SQUARE_SIZE // 4)
        if is_selected:
            pygame.draw.circle(screen, BLACK, position, SQUARE_SIZE // 4, 2)

def draw_message(message, color=BLACK, is_main_menu=False):
    textsurface = myfont.render(message, False, color)
    screen.blit(textsurface, (WINDOW_SIZE // 2 - textsurface.get_width() // 2, WINDOW_SIZE + TEXT_MARGIN))
    if is_main_menu:
        main_menu_button = myfont.render("Main Menu", False, BLACK)
        screen.blit(main_menu_button, (WINDOW_SIZE // 2 - main_menu_button.get_width() // 2, WINDOW_SIZE + TEXT_MARGIN + textsurface.get_height() + 20))
    pygame.display.update()


def draw_colored_message(message_parts):
    x_offset = 0
    surfaces = [(myfont.render(message, False, color), color) for message, color in message_parts]
    for surface, color in surfaces:
        x = WINDOW_SIZE // 2 - sum(part[0].get_width() for part in surfaces) // 2 + x_offset
        screen.blit(surface, (x, WINDOW_SIZE + TEXT_MARGIN))
        x_offset += surface.get_width()

def is_adjacent_move(src, dst):
    row_diff = abs(src[0] - dst[0])
    col_diff = abs(src[1] - dst[1])

    if (row_diff == 1 and col_diff == 0) or (row_diff == 0 and col_diff == 1):
        return True

    corners = [(0, 0), (2, 0), (0, 2), (2, 2)]
    center = (1, 1)
    if src in corners and dst == center:
        return True
    if dst in corners and src == center:
        return True

    return False

def check_winner(board):
    
    for i in range(3):
        if board[i][0] == board[i][1] == board[i][2] != '-' or board[0][i] == board[1][i] == board[2][i] != '-':
            return board[i][0]
    
    if board[0][0] == board[1][1] == board[2][2] != '-' or board[0][2] == board[1][1] == board[2][0] != '-':
        return board[1][1]
    return None

def get_empty_positions(board):
    empty_positions = []
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            if board[row][col] == '-':
                empty_positions.append((row, col))
    return empty_positions


def initialize_board():
    return [['-' for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]

class Button:
    def __init__(self, x, y, width, height, text, text_color, color, hover_color):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.text_color = text_color
        self.color = color
        self.hover_color = hover_color

    def draw(self, surface):
        mouse = pygame.mouse.get_pos()
        if self.x < mouse[0] < self.x + self.width and self.y < mouse[1] < self.y + self.height:
            pygame.draw.rect(surface, self.hover_color, (self.x, self.y, self.width, self.height))
        else:
            pygame.draw.rect(surface, self.color, (self.x, self.y, self.width, self.height))

        font = pygame.font.Font(None, 36)
        text = font.render(self.text, True, self.text_color)
        text_rect = text.get_rect(center=(self.x + self.width // 2, self.y + self.height // 2))
        surface.blit(text, text_rect)

    def is_clicked(self, x, y):
        return self.x < x < self.x + self.width and self.y < y < self.y + self.height

def evaluate_board(board, player):
    opponent = 'X' if player == 'O' else 'O'
    player_score = count_potential_wins(board, player)
    opponent_score = count_potential_wins(board, opponent)

    if opponent_score > 0:
        return -1000  

    return player_score - opponent_score


def count_potential_wins(board, player):
    count = 0
    lines = []

    for i in range(3):
        lines.append(board[i])
        lines.append([board[0][i], board[1][i], board[2][i]])

    lines.append([board[0][0], board[1][1], board[2][2]])
    lines.append([board[0][2], board[1][1], board[2][0]])

    for line in lines:
        if line.count(player) == 2 and line.count('-') == 1:
            count += 1

    return count

def minimax(board, depth, max_depth, maximizing_player, player, alpha, beta):
    if depth == max_depth or check_winner(board):
        return evaluate_board(board, player)

    if maximizing_player:
        max_eval = -float('inf')
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if board[row][col] == '-':
                    board[row][col] = player
                    eval = minimax(board, depth + 1, max_depth, False, player, alpha, beta)
                    board[row][col] = '-'
                    max_eval = max(max_eval, eval)
                    alpha = max(alpha, eval)
                    if beta <= alpha:
                        break
        return max_eval
    else:
        min_eval = float('inf')
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if board[row][col] == '-':
                    board[row][col] = ('X' if player == 'O' else 'O')
                    eval = minimax(board, depth + 1, max_depth, True, player, alpha, beta)
                    board[row][col] = '-'
                    min_eval = min(min_eval, eval)
                    beta = min(beta, eval)
                    if beta <= alpha:
                        break
        return min_eval

def computer_move(board, comp_pieces_placed, phase):
    best_move = ((-1, -1), (-1, -1))
    best_value = -float('inf')

    if phase == "placing":
        for i in range(len(board)):
            for j in range(len(board[i])):
                if board[i][j] == '-':
                    board[i][j] = 'O'
                    move_value = evaluate_board(board, 'O') 
                    board[i][j] = '-'
                    if move_value > best_value:
                        best_value = move_value
                        best_move = ((-1, -1), (i, j))
        return best_move

    for i in range(len(board)):
        for j in range(len(board[i])):
            if board[i][j] == '-':
                for k in range(len(board)):
                    for l in range(len(board[k])):
                        if board[k][l] == 'O' and is_adjacent_move((k, l), (i, j)):
                            board[k][l] = '-'
                            board[i][j] = 'O'
                            move_value = minimax(board, 0, 12, False, 'O', -float('inf'), float('inf'))
                            board[i][j] = '-'
                            board[k][l] = 'O'
                            if move_value > best_value:
                                best_value = move_value
                                best_move = ((k, l), (i, j))

    return best_move

def choose_starting_player():
    menu = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE + TEXT_AREA_HEIGHT))
    pygame.display.set_caption("Three Men's Morris - Choose Starting Player")

    option_font = pygame.font.SysFont('Comic Sans MS', 45)

    running = True
    while running:
        menu.fill(DISCORD_GRAY)
        player_starts = option_font.render("Player Starts", True, BLACK)
        computer_starts = option_font.render("Computer Starts", True, BLACK)
        x, y = pygame.mouse.get_pos()

        if 250 <= y <= 250 + player_starts.get_height() and WINDOW_SIZE // 2 - player_starts.get_width() // 2 <= x <= WINDOW_SIZE // 2 + player_starts.get_width() // 2:
            player_starts = option_font.render("Player Starts", True, BLUE)
        if 350 <= y <= 350 + computer_starts.get_height() and WINDOW_SIZE // 2 - computer_starts.get_width() // 2 <= x <= WINDOW_SIZE // 2 + computer_starts.get_width() // 2:
            computer_starts = option_font.render("Computer Starts", True, BLUE)

        menu.blit(player_starts, (WINDOW_SIZE // 2 - player_starts.get_width() // 2, 250))
        menu.blit(computer_starts, (WINDOW_SIZE // 2 - computer_starts.get_width() // 2, 350))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                if 250 <= y <= 250 + player_starts.get_height() and WINDOW_SIZE // 2 - player_starts.get_width() // 2 <= x <= WINDOW_SIZE // 2 + player_starts.get_width() // 2:
                    return 'X'
                if 350 <= y <= 350 + computer_starts.get_height() and WINDOW_SIZE // 2 - computer_starts.get_width() // 2 <= x <= WINDOW_SIZE // 2 + computer_starts.get_width() // 2:
                    return 'O'

def game(starting_player='X'):
    global BOARD #Inicialize speles laukumu
    BOARD = initialize_board()
    #Galvenais izvelnes pogas izveide
    main_menu_button = Button((WIDTH - 150) // 2, (HEIGHT - (BOARD_SIZE * SQUARE_SIZE + MARGIN)) // 2 + BOARD_SIZE * SQUARE_SIZE + MARGIN, 150, 50, "Menu", BLACK, GRAY, BLUE)
    # Speles mainigie
    current_player = starting_player
    phase = "placing"
    pieces_placed = 0
    comp_pieces_placed = 0
    selected_piece = None
    winner = None
    running = True

    #speles loop
    while running: 
        screen.fill(DISCORD_GRAY)
        draw_board()
        if selected_piece:
            draw_piece(selected_piece[0], selected_piece[1], BOARD[selected_piece[0]][selected_piece[1]], is_selected=True)
        if winner:
            if winner == 'X':
                draw_colored_message([("Red", RED), (" wins!", BLACK)])
            else:
                draw_colored_message([("Blue", BLUE), (" wins!", BLACK)])
            main_menu_button.draw(screen)
        else:
            if current_player == 'X':
                draw_colored_message([("Red", RED), ("'s turn", BLACK)])
            else:
                draw_colored_message([("Blue", BLUE), ("'s turn", BLACK)])
        pygame.display.update()

        if not winner and current_player == 'O' and comp_pieces_placed < 3:
            comp_move = computer_move(BOARD, comp_pieces_placed, phase)
            _, (to_row, to_col) = comp_move
            BOARD[to_row][to_col] = 'O'
            comp_pieces_placed += 1
            pieces_placed += 1
            if check_winner(BOARD):
                winner = current_player
            current_player = 'X'
            if pieces_placed == 6:
                phase = "moving"
            pygame.time.delay(500)
            draw_board()
            pygame.display.update()

        elif not winner and current_player == 'O' and comp_pieces_placed >= 3:
            comp_move = computer_move(BOARD, comp_pieces_placed, phase)
            (from_row, from_col), (to_row, to_col) = comp_move

            from_row, from_col = None, None
            for row in range(BOARD_SIZE):
                for col in range(BOARD_SIZE):
                    if BOARD[row][col] == 'O' and is_adjacent_move((row, col), (to_row, to_col)):
                        from_row, from_col = row, col
                        break
                else:
                    continue
                break
            print(f"Computer move: {comp_move}, from: ({from_row}, {from_col}), to: ({to_row}, {to_col})")

            if from_row is not None and from_col is not None:
                BOARD[from_row][from_col] = '-'
                BOARD[to_row][to_col] = 'O'
                if check_winner(BOARD):
                    winner = current_player
                current_player = 'X'
                pygame.time.delay(500)
                draw_board()
                pygame.display.update()
                


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                if winner and main_menu_button.is_clicked(x, y):
                    return
            if event.type == pygame.MOUSEBUTTONDOWN and not winner and current_player == 'X':
                x, y = pygame.mouse.get_pos()
                if winner and main_menu_button.is_clicked(x, y):
                    return
                col, row = (x - MARGIN) // SQUARE_SIZE, (y - MARGIN) // SQUARE_SIZE
                if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
                    if phase == "placing":
                        if BOARD[row][col] == '-':
                            BOARD[row][col] = current_player
                            pieces_placed += 1
                            if check_winner(BOARD):
                                winner = current_player
                            current_player = 'O' if current_player == 'X' else 'X'
                            if pieces_placed == 6:
                                phase = "moving"

                    elif phase == "moving":
                        if not selected_piece and BOARD[row][col] == current_player:
                            selected_piece = (row, col)
                        elif selected_piece and BOARD[row][col] == current_player:
                            selected_piece = (row, col)
                        elif selected_piece and BOARD[row][col] == '-' and is_adjacent_move(selected_piece, (row, col)):
                            BOARD[selected_piece[0]][selected_piece[1]] = '-'
                            BOARD[row][col] = current_player
                            if check_winner(BOARD):
                                winner = current_player
                            current_player = 'O' if current_player == 'X' else 'X'
                            selected_piece = None

    pygame.quit()
    sys.exit()


def main_menu():

    menu = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE + TEXT_AREA_HEIGHT))
    pygame.display.set_caption("Three Men's Morris - Main Menu")
    title_font = pygame.font.SysFont('Comic Sans MS', 70)
    option_font = pygame.font.SysFont('Comic Sans MS', 45)

    title = title_font.render("Three Men's Morris", True, BLACK)

    running = True
    while running:
        menu.fill(DISCORD_GRAY)
        start_game = option_font.render("Start Game", True, BLACK)
        instructions = option_font.render("Instructions", True, BLACK)
        quit_game = option_font.render("Quit Game", True, BLACK)
        x, y = pygame.mouse.get_pos()

        if 450 <= y <= 450 + quit_game.get_height() and WINDOW_SIZE // 2 - quit_game.get_width() // 2 <= x <= WINDOW_SIZE // 2 + quit_game.get_width() // 2:
            quit_game = option_font.render("Quit Game", True, BLUE)

        x, y = pygame.mouse.get_pos()
        if 250 <= y <= 250 + start_game.get_height() and WINDOW_SIZE // 2 - start_game.get_width() // 2 <= x <= WINDOW_SIZE // 2 + start_game.get_width() // 2:
            start_game = option_font.render("Start Game", True, BLUE)
        if 350 <= y <= 350 + instructions.get_height() and WINDOW_SIZE // 2 - instructions.get_width() // 2 <= x <= WINDOW_SIZE // 2 + instructions.get_width() // 2:
            instructions = option_font.render("Instructions", True, BLUE)

        menu.blit(title, (WINDOW_SIZE // 2 - title.get_width() // 2, 50))
        menu.blit(start_game, (WINDOW_SIZE // 2 - start_game.get_width() // 2, 250))
        menu.blit(instructions, (WINDOW_SIZE // 2 - instructions.get_width() // 2, 350))
        menu.blit(quit_game, (WINDOW_SIZE // 2 - quit_game.get_width() // 2, 450))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                if 250 <= y <= 250 + start_game.get_height() and WINDOW_SIZE // 2 - start_game.get_width() // 2 <= x <= WINDOW_SIZE // 2 + start_game.get_width() // 2:
                    starting_player = choose_starting_player()
                    game(starting_player)
                
                if 350 <= y <= 350 + instructions.get_height():
                    if WINDOW_SIZE // 2 - instructions.get_width() // 2 <= x <= WINDOW_SIZE // 2 + instructions.get_width() // 2:
                        show_instructions()
                        main_menu()
                if 450 <= y <= 450 + quit_game.get_height():
                    if WINDOW_SIZE // 2 - quit_game.get_width() // 2 <= x <= WINDOW_SIZE // 2 + quit_game.get_width() // 2:
                        running = False
                        pygame.quit()
                        sys.exit()

    pygame.quit()
    sys.exit()

def show_instructions():
    instructions = (
        "Three Men's Morris ir divu speletaju strategijas spele.\n"
        "\n"
        "Noteikumi:\n"
        "1. Katram speletajam ir 3 kaulini. Pirmajam speletajam 3 sarkani. Otrajam 3 zili. (O).\n"
        "2. Spele sakas ar kaulinu novietasanas fazi. Speletaji novieto savus kaulinus uz speles laukuma.\n"
        "3. Kad visi 6 kaulini atrodas uz speles laukuma, speletaji turpmakos gajienos tos pa vienam kaulinam var parvietot pa speles laukumu.\n"
        "4. Speletajs uzvar, kad tas ir izveidojis horizontalu, vertikalu vai diognalu liniju ar visiem 3 saviem kauliniem.\n"
        "5. Parvietosanas gajiens ir par vienu rutinu. Diognali ir iespejams parvietoties tikai no speles laukuma sturiem uz centru un atpakal\n"
    )

    tk.messagebox.showinfo("Instructions", instructions)

if __name__ == '__main__':
    main_menu()

