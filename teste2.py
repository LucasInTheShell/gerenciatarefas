import tkinter as tk
from tkinter import messagebox, filedialog
from datetime import datetime, timedelta
import json
import pandas as pd

class Tarefa:
    def _init_(self, cliente, descricao):
        self.cliente = cliente
        self.descricao = descricao
        self.intervalos = []
        self.ativo = False
        self.inicio_temp = None
        self.finalizado = False

    def iniciar(self):
        if self.finalizado:
            return
        if not self.ativo:
            self.inicio_temp = datetime.now()
            self.ativo = True

    def pausar(self):
        if self.ativo:
            fim = datetime.now()
            self.intervalos.append((self.inicio_temp, fim))
            self.ativo = False

    def finalizar(self):
        if self.ativo:
            self.pausar()
        self.finalizado = True

    def tempo_total(self):
        total = timedelta()
        for inicio, fim in self.intervalos:
            total += (fim - inicio)
        if self.ativo:
            total += (datetime.now() - self.inicio_temp)
        return total

    def to_dict(self):
        return {
            "cliente": self.cliente,
            "descricao": self.descricao,
            "tempo_total": str(self.tempo_total()).split('.')[0],
            "status": "Finalizada" if self.finalizado else ("Ativa" if self.ativo else "Pausada")
        }

tarefas = []
lista = []
tempo_ativo = []

def atualizar_lista():
    lista.delete(0, tk.END)
    for i, t in enumerate(tarefas):
        tempo = str(t.tempo_total()).split('.')[0]
        status = "Finalizada" if t.finalizado else ("Ativa" if t.ativo else "Pausada")
        lista.insert(tk.END, f"{i} - {t.cliente} | {t.descricao} | {status} | {tempo}")

def criar_tarefa():
    cliente = entrada_cliente.get()
    desc = entrada_desc.get()
    if cliente and desc:
        tarefas.append(Tarefa(cliente, desc))
        entrada_cliente.delete(0, tk.END)
        entrada_desc.delete(0, tk.END)
        atualizar_lista()
    else:
        messagebox.showwarning("Campos vazios", "Preencha cliente e descrição.")

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

def exportar_json_excel():
    dados = [t.to_dict() for t in tarefas]

    caminho_json = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")], title="Salvar como JSON")
    if caminho_json:
        with open(caminho_json, "w") as f:
            json.dump(dados, f, indent=4)

    caminho_excel = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")], title="Salvar como Excel")
    if caminho_excel:
        df = pd.DataFrame(dados)
        df.to_excel(caminho_excel, index=False)

    if caminho_json or caminho_excel:
        messagebox.showinfo("Exportado", "Exportação concluída com sucesso!")

def atualizar_temporizador():
    for t in tarefas:
        if t.ativo:
            agora = datetime.now()
            total = t.tempo_total()
            tempo_ativo.set(f"Tempo atual da tarefa ativa: {str(total).split('.')[0]}")
            break
    else:
        tempo_ativo.set("Tempo atual da tarefa ativa: 00:00:00")
    janela.after(1000, atualizar_temporizador)

# Interface Tkinter
janela = tk.Tk()
janela.title("Controle de Tarefas")

tk.Label(janela, text="Cliente:").grid(row=0, column=0)
entrada_cliente = tk.Entry(janela)
entrada_cliente.grid(row=0, column=1)

tk.Label(janela, text="Descrição:").grid(row=1, column=0)
entrada_desc = tk.Entry(janela)
entrada_desc.grid(row=1, column=1)

tk.Button(janela, text="Criar Tarefa", command=criar_tarefa).grid(row=0, column=2, rowspan=2, sticky="ns")

lista = tk.Listbox(janela, width=80)
lista.grid(row=2, column=0, columnspan=3)

tk.Button(janela, text="Iniciar", command=lambda: acao_tarefa('iniciar')).grid(row=3, column=0)
tk.Button(janela, text="Pausar", command=lambda: acao_tarefa('pausar')).grid(row=3, column=1)
tk.Button(janela, text="Finalizar", command=lambda: acao_tarefa('finalizar')).grid(row=3, column=2)

tk.Button(janela, text="Exportar JSON + Excel", command=exportar_json_excel).grid(row=4, column=0, columnspan=3, pady=10)

tempo_ativo = tk.StringVar()
tempo_ativo.set("Tempo atual da tarefa ativa: 00:00:00")
tk.Label(janela, textvariable=tempo_ativo, fg="blue", font=("Arial", 12)).grid(row=5, column=0, columnspan=3, pady=5)

atualizar_temporizador()
janela.mainloop()