'''Videojuego Coffee Shop
El videojuego consiste en preparar 5 ordenes aleatorias para ganar monedas y ganar dinero. 
Dependiendo el dinero ganado, se generará el número de estrellas al finalizar el juego.
Las ordenes consisten en un contenedor, líquido (leche o sin ésta), expreso, y complemento (azúcar y/o espuma),
el jugador tendrá que moverse a través de su espacio para preparar la orden y luego entregarla en la barra. '''
import pygame
import random

# Inicializar Pygame
pygame.init()
pygame.mixer.init()  # Inicializa el módulo de audio

# Configuración de la pantalla
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 500
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Coffee Shop')

# Colores a utilizar
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Cargar imágenes extras
background = pygame.image.load('images/background.png').convert()
shortcuts = pygame.image.load('images/shortcuts.png').convert_alpha()

#Recursos de botón que muestra imagen de ayuda
button_img = pygame.image.load('images/button.png').convert_alpha()
active_button = pygame.image.load('images/active_button.png').convert_alpha()
help_image = pygame.image.load('images/menu.png').convert()
help_popup = help_image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

# Música de fondo (larga duración)
pygame.mixer.music.load("audio/background_music.wav")  

# Imágenes que obtiene el jugador
cup_image = pygame.image.load('images/empty_cup.png').convert_alpha()
coffee_image = pygame.image.load('images/expresso.png').convert_alpha()
milk_image = pygame.image.load('images/coffee_w_milk.png').convert_alpha()
sugar_image = pygame.image.load('images/coffee_w_sugar.png').convert_alpha()
foam_image = pygame.image.load('images/coffee_w_foam.png').convert_alpha()

# Cargar imágenes de la mesa e iconos
img_table = pygame.image.load('images/table.png').convert_alpha()
cup_icon = pygame.image.load('images/cup_icon.png').convert_alpha()
coffee_pot = pygame.image.load('images/coffee_pot.png').convert_alpha()
milk_icon = pygame.image.load('images/milk_icon.png').convert_alpha()
sugar_icon = pygame.image.load('images/sugar_icon.png').convert_alpha()
cream_icon = pygame.image.load('images/cream_icon.png').convert_alpha()

#Sprites del jugador
player_images = {
    "front": pygame.image.load("images/player_front.png").convert_alpha(),
    "back": pygame.image.load("images/player_back.png").convert_alpha(),
    "right": pygame.image.load("images/player_right.png").convert_alpha(),
    "left": pygame.image.load("images/player_left.png").convert_alpha(),
}

# Fuente para texto
font = pygame.font.Font('fonts/Minecraft.ttf', 36)

# Clase para las mesas
class Table:
    def __init__(self, x, y, item_type, item_image, img_relate):
        self.x = x
        self.y = y
        self.image = img_table
        self.rect = self.image.get_rect(topleft=(self.x, self.y))
        self.item_type = item_type  # Tipo de objeto que otorga (taza, café, leche, azúcar y espuma.)
        self.item_image = item_image  # Imagen del objeto
        self.img_relate = img_relate
        self.img_relate_pos = (self.x + 180, self.y + 160)
        self.button_width = 120
        self.button_height = 50
        self.button_rect = pygame.Rect(
            self.x + 180,  
            self.y + 140,  
            self.button_width,
            self.button_height
        )
    def draw(self, screen):
        screen.blit(self.image, self.rect)
        pygame.draw.rect(screen, RED, self.button_rect, 2)
        screen.blit(self.img_relate, self.img_relate_pos)

# Clase del jugador
class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 5
        self.direction = "front"  # Dirección inicial
        self.image = player_images[self.direction]  # Imagen actual
        self.rect = self.image.get_rect(topleft=(self.x, self.y))
        self.inventory = []  # Inventario del jugador
        self.held_item = None  # Objeto que el jugador tiene en la mano

    def change_direction(self, direction):
        # Cambiar la dirección y la imagen del jugador
        self.direction = direction
        self.image = player_images[self.direction]

    def move(self, dx, dy):
        new_x = self.x + dx * self.speed
        new_y = self.y + dy * self.speed

        # Limitar el movimiento dentro de la pantalla
        if 0 <= new_x <= SCREEN_WIDTH - self.rect.width:
            self.x = new_x
        if 0 <= new_y <= SCREEN_HEIGHT - self.rect.height:
            self.y = new_y

        self.rect.topleft = (self.x, self.y)

    def draw(self):
        screen.blit(self.image, self.rect)
        # Dibujar el objeto que el jugador tiene en la mano
        if self.held_item:
            screen.blit(self.held_item, (self.x + 20, self.y + 40))  # Ajusta la posición según sea necesario

#Clase para mostrar un mensaje de error si se entrega un pedido mal
class Message:
    def __init__(self):
        self.message = ""
        self.show = False
        self.duration = 0
        self.max_duration = 60  # Duración en frames (1 segundo si el juego va a 60 FPS)

    def set_message(self, message):  
        self.message = message
        self.show = True
        self.duration = self.max_duration

    def update(self):
        if self.show and self.duration > 0:
            self.duration -= 1
        else:
            self.show = False

    def draw(self):
        if self.show:
            text = font.render(self.message, True, BLACK)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            pygame.draw.rect(screen, WHITE, text_rect.inflate(20, 10))
            screen.blit(text, text_rect)


# Función para verificar si el jugador está en el área del botón
def is_near_button(player_rect, button_rect):
    return player_rect.colliderect(button_rect)

# Clase para los pedidos
class Order:
    def __init__(self):
        self.possible_orders = self.orders()  # Diccionario de órdenes
        self.order_name = random.choice(list(self.possible_orders.keys()))  # Nombre del pedido
        self.coffee_type = self.possible_orders[self.order_name]  # Ingredientes del pedido

    def orders(self):
        return {
            "Americano": ["taza", "cafe"],
            "Latte": ["taza", "cafe", "leche"],
            "Cafe con azucar": ["taza", "cafe", "azucar"],
            "Capuchino": ["taza", "cafe", "espuma"],
            "Latte con espuma": ["taza", "cafe", "leche", "espuma"]
        }


    def draw(self, x, y):
        text = font.render(f"Pedido: {self.order_name}", True, BLACK)
        text_rect = text.get_rect(topleft=(50, 50))
        pygame.draw.rect(screen, WHITE, text_rect.inflate(20, 10)) 
        screen.blit(text, text_rect)  # Dibuja el texto encima

# Crear varias mesas
tables = [
    Table(-150, 200, "taza", cup_image, cup_icon),  # Mesa de tazas
    Table(100, 0, "cafe", coffee_image, coffee_pot),  # Mesa de café
    Table(280, 0, "leche", milk_image, milk_icon),  # Mesa de leche
    Table(100, 200, "azucar", sugar_image, sugar_icon),  # Mesa de azúcar
    Table(280, 200, "espuma", foam_image, cream_icon)  # Mesa de espuma
]

# Función principal del juego
def main():
    clock = pygame.time.Clock()
    player = Player(120, 150)
    show_popup = False
    current_button_image = button_img
    message = Message()  # Generador de mensaje en la pantalla
    pygame.mixer.music.play(-1)  # Música en bucle
    pygame.mixer.music.set_volume(0.5)  # Volumen al 50%

    #Verificar lógica del juego
    orders = [Order() for _ in range(5)]  # 5 pedidos
    current_order = 0
    coins = 0
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:  # Detectar tecla presionada
                if event.key == pygame.K_s:   # Si es la tecla S
                    # Verificar si el inventario coincide con el pedido actual
                    if current_order < len(orders):
                        if set(player.inventory) == set(orders[current_order].coffee_type):
                            coins += 1
                            current_order += 1
                            player.inventory = []  # Reiniciar inventario
                            player.held_item = None  # Limpiar objeto en mano
                            message.set_message("Pedido completado.") 
                            print(f"¡Pedido completado! Monedas: {coins}")
                        else:
                            message.set_message("¡Error! El pedido no coincide.") 
                            coins -= 1
                            print("¡Error! El pedido no coincide.")
                elif event.key == pygame.K_c: #Borrar inventario
                    player.inventory = []
                    player.held_item = None
                elif event.key == pygame.K_q and not show_popup:  # Abrir imagen de ayuda
                    show_popup = True
                    current_button_image = active_button  # Cambia de imagen
                elif event.key == pygame.K_z and show_popup:  # Cerrar popup
                    show_popup = False
                    current_button_image = button_img  # Vuelve a la imagen normal
                elif event.key == pygame.K_x: #Salir del juego
                    running = False
        
        # Capturar las teclas presionadas
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0  # Cambios en X e Y

        if keys[pygame.K_UP]:  # Mover hacia arriba
            dy = -1
            player.change_direction('back')
        if keys[pygame.K_DOWN]:  # Mover hacia abajo
            dy = 1
            player.change_direction('front')
        if keys[pygame.K_LEFT]:  # Mover hacia la izquierda
            dx = -1
            player.change_direction('left')
        if keys[pygame.K_RIGHT]:  # Mover hacia la derecha
            dx = 1
            player.change_direction('right')
        
        # Mover al jugador
        player.move(dx, dy)
        
        # Verificar interacción con las mesas
        for table in tables:
            if is_near_button(player.rect, table.button_rect) and keys[pygame.K_a]:
                print(f"El jugador obtuvo: {table.item_type}")
                player.inventory.append(table.item_type)  # Añadir el objeto al inventario
                player.held_item = table.item_image  # Asignar la imagen del objeto al jugador

        # Dibujar fondo y mesas
        screen.blit(background, (0, 0))
        screen.blit(shortcuts, (0,150))
        for table in tables:
            table.draw(screen)  # Dibujar el área interactiva de cada mesa

        # Dibujar jugador
        player.draw()

        # Botón (esquina superior derecha)
        button_rect = current_button_image.get_rect(topright=(SCREEN_WIDTH - 10, 10))
        screen.blit(current_button_image, button_rect)
        
        # Popup con fondo semitransparente
        if show_popup:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))
            screen.blit(overlay, (0, 0))
            screen.blit(help_image, help_popup)

        #Actualizar mensaje de error
        message.update()  # Actualizar el temporizador
        message.draw()    # Dibujar el mensaje si está activo
        
        # Mostrar pedido actual
        if current_order < len(orders):
            orders[current_order].draw(50, 50)
        else:
            text = font.render("¡Fin del juego! Monedas: " + str(coins), True, BLACK)
            text_rect = text.get_rect(topleft=(50, 50))
            pygame.draw.rect(screen, WHITE, text_rect.inflate(20, 10))  
            screen.blit(text, text_rect)  # Dibuja el texto encima

        # Actualizar pantalla
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()