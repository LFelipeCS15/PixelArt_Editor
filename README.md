# Pixel Art Editor – Tkinter + Pillow

Este projeto é um editor simples de **Pixel Art**, desenvolvido em **Python**, utilizando `tkinter` como interface gráfica e `Pillow` para salvar as imagens em PNG.

---

## 🧰 Funcionalidades

* Desenho com lápis
* Borracha
* Balde de preenchimento
* Conta-gotas
* Undo / Redo
* Zoom
* Redimensionamento da grade
* Salvar como PNG

---

## 📌 Requisitos

Antes de rodar o programa, você precisará ter:

* **Python 3.8 ou superior**
* Pip (gerenciador de pacotes do Python)

---

## 📥 Instalando Dependências

1️⃣ **Abra o terminal (CMD, PowerShell ou Linux/macOS Terminal).**

2️⃣ Instale a biblioteca Pillow (necessária para salvar PNG):

```bash
pip install pillow
```

> A biblioteca `tkinter` já vem instalada com o Python na maioria das distribuições oficiais.
> Se ao rodar o código der erro de tkinter não encontrado, instale conforme seu sistema:

* **Windows:** já vem junto com o Python.
* **Ubuntu / Debian:**

  ```bash
  sudo apt-get install python3-tk
  ```
* **Arch:**

  ```bash
  sudo pacman -S tk
  ```

---

## ▶️ Executando o Programa

No terminal, estando dentro da pasta do projeto, execute:

```bash
python editor.py
```

O editor abrirá em uma janela com a grade de pixels e as ferramentas.

---

## 🖌 Como Usar

* **Clique** para desenhar usando a ferramenta selecionada
* **Caneta:** pinta pixels
* **Borracha:** volta o pixel para branco
* **Balde:** faz preenchimento estilo "paint"
* **Conta-gotas:** pega a cor do pixel
* **CTRL+Z / CTRL+Y:** Undo / Redo
* **Salvar PNG:** exporta a arte
* **Redim. Grade:** muda o tamanho do quadro
* **Zoom:** aumenta ou diminui o tamanho dos pixels na tela

---

## 📜 Licença

Este projeto pode ser utilizado livremente para fins educacionais, pessoais ou acadêmicos.

---

Bom desenho! 🎨🕹️
