import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime, timedelta
import json
import pandas as pd 

class Tarefa:
    def __init__(self, cliente, descricao):
        self.cliente = cliente
        self.descricao = descricao
        self.intervalos = []
        self.ativo = False
        self.inicio_temp = None
        self.finalizado = False
        self.historico = []  # Novo atributo para armazenar o histórico
    
    def iniciar(self):
        if self.finalizado:
            return
        if not self.ativo:
            self.inicio_temp = datetime.now()
            self.ativo = True
            # Registrar no histórico
            self.historico.append(f"Iniciada em: {self.inicio_temp.strftime('%H:%M:%S')}")

    def pausar(self):
        if self.ativo:
            fim = datetime.now()
            self.intervalos.append((self.inicio_temp, fim))
            self.ativo = False
            # Registrar no histórico
            self.historico.append(f"Pausada em: {fim.strftime('%H:%M:%S')}")

    def finalizar(self):
        if self.ativo:
            self.pausar()
        self.finalizado = True
        self.historico.append(f"Finalizada em: {datetime.now().strftime('%H:%M:%S')}")

    def tempo_total(self):
        total = timedelta()
        for inicio, fim in self.intervalos:
            total += (fim - inicio)
        return total
    
    def to_dict(self):
        return {
            "cliente": self.cliente,
            "descricao": self.descricao,
            "tempo_total": str(self.tempo_total()),
            "status": "Finalizada" if self.finalizado else ("Ativa" if self.ativo else "Pausada"),
            "historico": "\n".join(self.historico)  # Adicionando histórico ao exportar
        }

# Interface TKINTER
tarefas = []

def atualizar_lista():
    lista.delete(0, tk.END)
    for i, t in enumerate(tarefas):
        tempo = str(t.tempo_total()).split('.')[0]
        status = "Finalizada" if t.finalizado else ("Ativa" if t.ativo else "Pausada")
        
        # Configuração das cores baseadas no status
        if t.finalizado:
            bg_color = "#FFCCCC"  # Vermelho claro
        elif t.ativo:
            bg_color = "#CCFFCC"  # Verde claro
        else:
            bg_color = "#FFFFCC"  # Amarelo claro
            
        # Mostrar último evento do histórico se existir
        ultimo_evento = t.historico[-1] if t.historico else "Nenhum registro"
        lista.insert(tk.END, f"{i} - {t.cliente} | {t.descricao} | {status} | {tempo} | {ultimo_evento}")
        lista.itemconfig(tk.END, {'bg': bg_color})

def criar_tarefa():
    cliente = entrada_cliente.get()
    desc = entrada_desc.get()
    if cliente and desc:
        tarefas.append(Tarefa(cliente, desc))
        entrada_cliente.delete(0, tk.END)
        entrada_desc.delete(0, tk.END)
        atualizar_lista()

def acao_tarefa(tipo):
    try:
        idx = int(lista.get(lista.curselection()).split(' - ')[0])
        tarefa = tarefas[idx]
        if tipo == 'iniciar':
            tarefa.iniciar()
        elif tipo == 'pausar':
            tarefa.pausar()
        elif tipo == 'finalizar':
            tarefa.finalizar()
        atualizar_lista()
    except:
        messagebox.showerror("Erro", "Selecione uma tarefa válida.")

def mostrar_historico():
    try:
        idx = int(lista.get(lista.curselection()).split(' - ')[0])
        tarefa = tarefas[idx]
        historico_window = tk.Toplevel()
        historico_window.title(f"Histórico - {tarefa.cliente}")
        
        txt_historico = tk.Text(historico_window, width=50, height=15)
        txt_historico.pack(padx=10, pady=10)
        
        # Adiciona cada item do histórico
        for evento in tarefa.historico:
            txt_historico.insert(tk.END, evento + "\n")
        
        txt_historico.config(state=tk.DISABLED)  # Torna o texto somente leitura
    except:
        messagebox.showerror("Erro", "Selecione uma tarefa válida.")

def exportar_json_excel():
    dados = [t.to_dict() for t in tarefas]
    with open("tarefas.json", "w") as f:
        json.dump(dados, f, indent=4)
    df = pd.DataFrame(dados)
    df.to_excel("tarefa.xlsx", index=False)
    messagebox.showinfo("Exportado", "Dados exportados para tarefas.json e tarefas.xlsx")

# Configuração da janela principal
janela = tk.Tk()
janela.title("Controle de Tarefas")

# Adicionando um pouco de estilo
style = ttk.Style()
style.configure("TButton", padding=6)

# Widgets de entrada
tk.Label(janela, text="Cliente:").grid(row=0, column=0, padx=5, pady=5)
entrada_cliente = tk.Entry(janela, width=30)
entrada_cliente.grid(row=0, column=1, padx=5, pady=5)

tk.Label(janela, text="Descrição:").grid(row=1, column=0, padx=5, pady=5)
entrada_desc = tk.Entry(janela, width=30)
entrada_desc.grid(row=1, column=1, padx=5, pady=5)

# Botão de criar tarefa
btn_criar = ttk.Button(janela, text="Criar Tarefa", command=criar_tarefa)
btn_criar.grid(row=0, column=2, rowspan=2, padx=5, pady=5, sticky="ns")

# Lista de tarefas
lista = tk.Listbox(janela, width=100, height=15)
lista.grid(row=2, column=0, columnspan=4, padx=5, pady=5)

# Botões de controle
btn_iniciar = ttk.Button(janela, text="Iniciar", command=lambda: acao_tarefa('iniciar'))
btn_iniciar.grid(row=3, column=0, padx=5, pady=5, sticky="ew")

btn_pausar = ttk.Button(janela, text="Pausar", command=lambda: acao_tarefa('pausar'))
btn_pausar.grid(row=3, column=1, padx=5, pady=5, sticky="ew")

btn_finalizar = ttk.Button(janela, text="Finalizar", command=lambda: acao_tarefa('finalizar'))
btn_finalizar.grid(row=3, column=2, padx=5, pady=5, sticky="ew")

# Botão para ver histórico completo
btn_historico = ttk.Button(janela, text="Ver Histórico", command=mostrar_historico)
btn_historico.grid(row=3, column=3, padx=5, pady=5, sticky="ew")

# Botão de exportação
btn_exportar = ttk.Button(janela, text="Exportar JSON + Excel", command=exportar_json_excel)
btn_exportar.grid(row=4, column=0, columnspan=4, padx=5, pady=5, sticky="ew")

janela.mainloop()