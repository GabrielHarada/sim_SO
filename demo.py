import tkinter as tk
from tkinter import ttk, filedialog

def carregar_arquivo():
    caminho = filedialog.askopenfilename(
        title="Selecionar arquivo de configuração",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
    )
    if not caminho:
        return
    
    for item in tree.get_children():
        tree.delete(item)

    with open(caminho, "r", encoding="utf-8") as f:
        linhas = [linha.strip() for linha in f if linha.strip()]
    
    if len(linhas) < 2:
        print("Arquivo inválido.")
        return

    algoritmo, quantum = linhas[0].split(";")
    lbl_info["text"] = f"Algoritmo: {algoritmo} | Quantum: {quantum}"

    colunas = ["id", "cor", "ingresso", "duracao", "prioridade", "lista_eventos"]
    tree["columns"] = colunas
    tree["show"] = "headings"

    for col in colunas:
        tree.heading(col, text=col.capitalize())
        tree.column(col, width=100, anchor="center")

    for linha in linhas[1:]:
        valores = linha.split(";")
        if len(valores) == len(colunas):
            tree.insert("", "end", values=valores)
        else:
            print(f"Linha inválida ignorada: {linha}")

# --- Função para editar célula ---
def editar_celula(event):
    item = tree.identify_row(event.y)
    coluna = tree.identify_column(event.x)
    if not item or not coluna:
        return

    # Índice da coluna (ex: '#2' → 1)
    col_index = int(coluna.replace('#', '')) - 1
    valor_atual = tree.item(item, "values")[col_index]

    # Coordenadas da célula
    x, y, width, height = tree.bbox(item, coluna)
    
    # Cria um campo Entry sobre a célula
    entry = tk.Entry(tree)
    entry.place(x=x, y=y, width=width, height=height)
    entry.insert(0, valor_atual)
    entry.focus()

    def salvar_edicao(event=None):
        novo_valor = entry.get()
        valores = list(tree.item(item, "values"))
        valores[col_index] = novo_valor
        tree.item(item, values=valores)
        entry.destroy()

    def cancelar_edicao(event=None):
        entry.destroy()

    entry.bind("<Return>", salvar_edicao)
    entry.bind("<Escape>", cancelar_edicao)
    entry.bind("<FocusOut>", salvar_edicao)

# ==== GUI ====
root = tk.Tk()
root.title("Editor de Configuração de Escalonamento")
root.geometry("700x400")

lbl_info = ttk.Label(root, text="Nenhum arquivo carregado", font=("Arial", 12))
lbl_info.pack(pady=10)

btn_carregar = ttk.Button(root, text="Abrir arquivo .txt", command=carregar_arquivo)
btn_carregar.pack(pady=5)

frame_tabela = ttk.Frame(root)
frame_tabela.pack(fill=tk.BOTH, expand=True)

tree = ttk.Treeview(frame_tabela)
tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

scroll_y = ttk.Scrollbar(frame_tabela, orient=tk.VERTICAL, command=tree.yview)
scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
tree.configure(yscrollcommand=scroll_y.set)

# Permitir edição ao dar duplo clique
tree.bind("<Double-1>", editar_celula)

root.mainloop()
