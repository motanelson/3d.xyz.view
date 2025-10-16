# board3d_volume.py
# Mostra um tabuleiro 8x8 e um volume 8x8x8 de esferas azuis carregadas por loads(...)
# Requisitos: PyOpenGL, freeglut
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import sys
import os

# ---------- configurações ----------
GRID_SIZE = 8        # tabuleiro 8x8
VOL_Z = 8            # camadas em altura (8)
CELL = 1.0           # espaçamento x/y entre células
VERT_SPACING = 0.6   # espaçamento vertical entre camadas (z)
SPHERE_RADIUS = 0.18
CAM_DISTANCE = 14.0

window_width = 1000
window_height = 720

# cena
scene = None   # scene[z][y][x] (z = 0..VOL_Z-1)
num_z = VOL_Z

# rotação/zoom controles
yaw = 0.0
pitch = 25.0
zoom = CAM_DISTANCE

# ---------- Função loads (reaproveitada do teu ficheiro) ----------
# Esta versão espera um texto com frames separados por ';', linhas por '\n', células por ','.
# Cada "frame" corresponde a uma camada Z. A função devolve uma lista 3D [z][y][x].
def loads(texts):
    ll = True
    zi = 0
    xi = 0
    yi = 0
    a = []
    ttt = texts.split(";")
    zi = len(ttt)
    for t in range(zi):
        yyy = ttt[t].strip().split("\n")
        yi = len(yyy)
        for y in range(yi):
            xxx = yyy[y].split(",")
            xi = len(xxx)
            if ll:
                # cria array 3D: z x y x x
                a = [[[" " for _ in range(xi)] for _ in range(yi)] for _ in range(zi)]
                ll = False
            for x in range(xi):
                b = xxx[x].strip()
                if b == "":
                    a[t][y][x] = " "
                else:
                    a[t][y][x] = b
    return a

# (Fonte desta função: teu script carregado). :contentReference[oaicite:1]{index=1}

# ---------- utilidades de posição ----------
def world_pos_from_index(ix, iy, grid_size=GRID_SIZE, cell=CELL):
    HALF = grid_size * cell / 2.0
    wx = -HALF + (cell / 2.0) + ix * cell
    wz = -HALF + (cell / 2.0) + iy * cell
    return wx, wz

# ---------- OpenGL init ----------
def init_gl():
    glClearColor(1.0, 1.0, 0.0, 1.0)  # fundo amarelo
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_NORMALIZE)
    glShadeModel(GL_SMOOTH)

    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glLightfv(GL_LIGHT0, GL_POSITION, [4.0, 10.0, 6.0, 1.0])
    glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.9, 0.9, 0.9, 1.0])
    glLightfv(GL_LIGHT0, GL_SPECULAR, [0.6, 0.6, 0.6, 1.0])

# ---------- desenho do tabuleiro tipo xadrez (8x8) ----------
def draw_checkboard(grid_size=GRID_SIZE, cell=CELL):
    glDisable(GL_LIGHTING)
    half = (grid_size - 1) * cell / 2.0
    glBegin(GL_QUADS)
    for iy in range(grid_size):
        for ix in range(grid_size):
            wx = -half + ix * cell
            wz = -half + iy * cell
            if (ix + iy) % 2 == 0:
                glColor3f(0.88, 0.88, 0.88)
            else:
                glColor3f(1.0, 1.0, 0.2)
            # quad levemente elevado para evitar z-fighting
            y0 = 0.0
            y1 = 0.0
            glVertex3f(wx, y0, wz)
            glVertex3f(wx + cell, y0, wz)
            glVertex3f(wx + cell, y0, wz + cell)
            glVertex3f(wx, y0, wz + cell)
    glEnd()
    glEnable(GL_LIGHTING)

# ---------- desenhar volume de esferas azuis ----------
def draw_volume_spheres(volume):
    # volume[z][y][x]
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, [0.15, 0.15, 0.2, 1.0])
    glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 20.0)
    maxz = min(len(volume), VOL_Z)
    for iz in range(maxz):
        layer = volume[iz]
        rows = min(len(layer), GRID_SIZE)
        for iy in range(rows):
            cols = min(len(layer[iy]), GRID_SIZE)
            for ix in range(cols):
                if str(layer[iy][ix]).strip() != "":
                    wx, wz = world_pos_from_index(ix, iy)
                    # altura da esfera depende da camada iz
                    y = SPHERE_RADIUS + iz * VERT_SPACING
                    glPushMatrix()
                    glTranslatef(wx, y, wz)
                    glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, [0.05, 0.12, 0.9, 1.0])
                    glutSolidSphere(SPHERE_RADIUS, 20, 20)
                    glPopMatrix()

# ---------- display / camera ----------
def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    # câmera simples baseada em zoom / yaw / pitch
    eye_x = zoom * math.sin(math.radians(yaw)) * math.cos(math.radians(pitch))
    eye_y = zoom * math.sin(math.radians(pitch))
    eye_z = zoom * math.cos(math.radians(yaw)) * math.cos(math.radians(pitch))
    gluLookAt(eye_x, eye_y, eye_z, 0.0,  (VOL_Z * VERT_SPACING) / 4.0, 0.0, 0.0, 1.0, 0.0)

    # move o tabuleiro para baixo um pouco para ficar no fundo do ecrã
    glPushMatrix()
    glTranslatef(0.0, -1.5, 0.0)

    # grande plano amarelo de fundo por baixo do tabuleiro
    glDisable(GL_LIGHTING)
    glColor3f(1.0, 1.0, 0.6)
    half = GRID_SIZE * CELL / 2.0 + 4.0
    glBegin(GL_QUADS)
    glVertex3f(-half, -0.01, -half)
    glVertex3f(half, -0.01, -half)
    glVertex3f(half, -0.01, half)
    glVertex3f(-half, -0.01, half)
    glEnd()
    glEnable(GL_LIGHTING)

    # desenha tabuleiro e volume de esferas
    draw_checkboard()
    if scene:
        draw_volume_spheres(scene)

    glPopMatrix()
    glutSwapBuffers()

# ---------- controles ----------
import math
def keyboard(key, x, y):
    global yaw, pitch, zoom
    key = key.decode() if isinstance(key, bytes) else key
    if key == '\x1b' or key == 'q':
        sys.exit(0)
    elif key.lower() == 'a':
        yaw -= 8.0
    elif key.lower() == 'd':
        yaw += 8.0
    elif key.lower() == 'w':
        pitch = min(80.0, pitch + 5.0)
    elif key.lower() == 's':
        pitch = max(-10.0, pitch - 5.0)
    elif key == '+':
        zoom = max(4.0, zoom - 1.0)
    elif key == '-':
        zoom = min(40.0, zoom + 1.0)
    glutPostRedisplay()

def special_key(key, x, y):
    pass

def reshape(w, h):
    global window_width, window_height
    window_width = w
    window_height = h
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45.0, float(w) / float(h if h>0 else 1), 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)

# ---------- main ----------
def main():
    global scene, zoom, yaw, pitch
    # tenta abrir "my.xyz" ou procura algum .xyz no diretório
    fn = "my.xyz"
    if not os.path.exists(fn):
        # procura ficheiro .xyz carregado
        for f in os.listdir("."):
            if f.lower().endswith(".xyz") or f.lower().endswith(".xytb") or f.lower().endswith(".xyz.txt"):
                fn = f
                break

    if os.path.exists(fn):
        try:
            with open(fn, "r", encoding="utf-8") as fh:
                txt = fh.read()
            scene = loads(txt)
            print("Carregado:", fn, "-> dimensões (z,y,x):", len(scene), len(scene[0]) if scene else 0, len(scene[0][0]) if scene and scene[0] else 0)
        except Exception as e:
            print("Erro a ler", fn, e)
            scene = [[[" " for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)] for __ in range(VOL_Z)]
    else:
        # cria vazio 8x8x8
        scene = [[[" " for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)] for __ in range(VOL_Z)]
        print("Nenhum ficheiro .xyz encontrado. Criado volume vazio 8x8x8.")

    # inicia GLUT/OpenGL
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(window_width, window_height)
    glutCreateWindow(b"Volume 3D 8x8x8 - esferas azuis")
    init_gl()
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutKeyboardFunc(keyboard)
    glutSpecialFunc(special_key)
    glutIdleFunc(glutPostRedisplay)
    glutMainLoop()

if __name__ == "__main__":
    main()

