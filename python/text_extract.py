import tkinter as tk
import re

# 创建主窗口
root = tk.Tk()
root.title("文本处理")

# 设置窗口大小
root.geometry("1200x900")

# 让窗口的行列可伸缩
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

# 创建框架
frame = tk.Frame(root)
frame.grid(row=0, column=0, sticky="nsew")  # 让框架填充整个窗口

# 让框架的列可以伸缩
frame.columnconfigure(0, weight=1)
frame.columnconfigure(1, weight=1)
frame.rowconfigure(0, weight=1)


# 创建输入框（左侧）
input_area = tk.Text(frame, wrap=tk.WORD)
input_area.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")  # 让文本框填充空间

# 创建输出框（右侧）
output_area = tk.Text(frame, wrap=tk.WORD, state=tk.DISABLED)
output_area.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")  # 让文本框填充空间

# 创建一个按钮，点击按钮后可以获取用户输入的文本
def get_input():
    user_input = input_area.get("1.0", tk.END)  # 获取输入框中的内容
    
    # 处理每一行
    processed_lines = []
    for line in user_input.splitlines():
        if not line.strip():
            continue  # 跳过空行
        
        # 检查行尾是否有中文标点符号
        if re.search(r'[。！？；，：）】》’”]$', line.strip()):
            line = re.sub(r'^%', '', line)  # 删除行首 '%'
            processed_line = f"<p class=\"calibre24\">{line.strip()}</p>"
        else:
            processed_line = f"<p class=\"calibre18\"><span class=\"calibre22\">{line.strip()}</span></p>"
        
        processed_lines.append(processed_line)
    
    processed_text = "\n".join(processed_lines)  # 重新拼接文本

    # 显示处理后的文本
    output_area.config(state=tk.NORMAL)
    output_area.delete("1.0", tk.END)
    output_area.insert(tk.END, processed_text)
    output_area.config(state=tk.DISABLED)

    # 复制到剪贴板
    root.clipboard_clear()
    root.clipboard_append(processed_text)
    root.update()

    # 提示用户
    status_label.config(text="✅ 处理后的文本已复制到剪贴板！", fg="green")

# 创建按钮并放在新的一行
button = tk.Button(root, text="处理输入", command=get_input)
# 让按钮在 **第 1 行**，**第 1 列**（占 1 列，不跨 2 列）
button.grid(row=1, column=0, columnspan=1, pady=10, padx=30, sticky="ew")

# 让按钮的行可以伸缩
root.rowconfigure(1, weight=0)

# 创建状态提示标签
status_label = tk.Label(root, text="", fg="black")
status_label.grid(row=2, column=0, columnspan=2, pady=5)


# 运行窗口
root.mainloop()
