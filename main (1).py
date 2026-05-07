import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime
import urllib.request
import urllib.error
import urllib.parse

class WebSiteManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Менеджер данных веб-сайта")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Файл для избранного (сохранённые записи)
        self.favorites_file = "favorites.json"
        self.favorites = self.load_favorites()
        
        # Базовый URL API вашего веб-сайта (ЗАМЕНИТЕ НА СВОЙ)
        self.api_base_url = "https://jsonplaceholder.typicode.com"
        
        # Создание интерфейса
        self.create_widgets()
        
        # Привязка клавиши Enter
        self.search_entry.bind("<Return>", lambda event: self.search_data())
    
    def create_widgets(self):
        # Верхняя панель с поиском
        search_frame = ttk.Frame(self.root, padding="10")
        search_frame.pack(fill=tk.X)
        
        ttk.Label(search_frame, text="Поиск:").pack(side=tk.LEFT)
        
        self.search_entry = ttk.Entry(search_frame, width=40, font=("Arial", 12))
        self.search_entry.pack(side=tk.LEFT, padx=(10, 10), fill=tk.X, expand=True)
        
        self.search_btn = ttk.Button(search_frame, text="🔍 Найти", command=self.search_data)
        self.search_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.favorites_btn = ttk.Button(search_frame, text="⭐ Избранное", command=self.show_favorites)
        self.favorites_btn.pack(side=tk.LEFT)
        
        # Основная область
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Результаты поиска
        left_frame = ttk.LabelFrame(main_frame, text="Результаты поиска", padding="5")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        self.results_listbox = tk.Listbox(left_frame, height=20, font=("Arial", 10))
        self.results_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        results_scrollbar = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.results_listbox.yview)
        results_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.results_listbox.config(yscrollcommand=results_scrollbar.set)
        
        results_btn_frame = ttk.Frame(left_frame)
        results_btn_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Button(results_btn_frame, text="➕ Добавить в избранное", 
                  command=self.add_to_favorites_from_results).pack(side=tk.LEFT, padx=5)
        ttk.Button(results_btn_frame, text="👤 Просмотреть детали", 
                  command=self.view_details_from_results).pack(side=tk.LEFT, padx=5)
        
        # Избранное
        right_frame = ttk.LabelFrame(main_frame, text="⭐ Избранное", padding="5")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        self.favorites_listbox = tk.Listbox(right_frame, height=20, font=("Arial", 10))
        self.favorites_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        fav_scrollbar = ttk.Scrollbar(right_frame, orient=tk.VERTICAL, command=self.favorites_listbox.yview)
        fav_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.favorites_listbox.config(yscrollcommand=fav_scrollbar.set)
        
        fav_btn_frame = ttk.Frame(right_frame)
        fav_btn_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Button(fav_btn_frame, text="❌ Удалить из избранного", 
                  command=self.remove_from_favorites).pack(side=tk.LEFT, padx=5)
        ttk.Button(fav_btn_frame, text="👤 Просмотреть детали", 
                  command=self.view_details_from_favorites).pack(side=tk.LEFT, padx=5)
        
        # Статус-бар
        self.status_var = tk.StringVar()
        self.status_var.set("Готов к работе")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    # ---------- Работа с избранным ----------
    def load_favorites(self):
        if os.path.exists(self.favorites_file):
            try:
                with open(self.favorites_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_favorites(self):
        with open(self.favorites_file, 'w', encoding='utf-8') as f:
            json.dump(self.favorites, f, ensure_ascii=False, indent=2)
        self.update_favorites_display()
    
    def update_favorites_display(self):
        self.favorites_listbox.delete(0, tk.END)
        for item_id, data in self.favorites.items():
            display_text = f"{data.get('title', data.get('name', 'Без названия'))} [ID: {item_id}]"
            self.favorites_listbox.insert(tk.END, display_text)
    
    # ---------- API запросы (универсальные) ----------
    def make_api_request(self, url):
        try:
            req = urllib.request.Request(url)
            req.add_header('Accept', 'application/json')
            req.add_header('User-Agent', 'WebSite-Manager/1.0')
            
            with urllib.request.urlopen(req, timeout=10) as response:
                data = response.read()
                return json.loads(data.decode('utf-8'))
        except urllib.error.HTTPError as e:
            raise Exception(f"HTTP ошибка: {e.code}")
        except urllib.error.URLError as e:
            raise Exception(f"Ошибка соединения: {e.reason}")
        except Exception as e:
            raise Exception(f"Ошибка: {str(e)}")
    
    # ---------- Логика поиска (адаптируйте под своё API) ----------
    def search_data(self):
        """Поиск данных на вашем веб-сайте через API"""
        query = self.search_entry.get().strip()
        
        if not query:
            messagebox.showwarning("Предупреждение", "Введите поисковый запрос!")
            self.status_var.set("Ошибка: пустой запрос")
            return
        
        self.status_var.set(f"Поиск: {query}...")
        
        try:
            # ПРИМЕР: для JSONPlaceholder ищем пользователей по имени или email
            # Замените URL и логику под своё API
            encoded_query = urllib.parse.quote(query)
            # В этом API поиск происходит через фильтр ?q=...
            url = f"{self.api_base_url}/users?q={encoded_query}"
            # На самом деле JSONPlaceholder не поддерживает поиск, поэтому просто получим всех
            # и отфильтруем вручную (для демонстрации)
            all_items = self.make_api_request(f"{self.api_base_url}/users")
            
            # Фильтрация (ищем совпадение в name, username или email)
            filtered = []
            for item in all_items:
                if (query.lower() in item.get('name', '').lower() or
                    query.lower() in item.get('username', '').lower() or
                    query.lower() in item.get('email', '').lower()):
                    filtered.append(item)
            
            self.results_listbox.delete(0, tk.END)
            
            if filtered:
                for item in filtered:
                    display_text = f"{item.get('name')} (@{item.get('username')}) - {item.get('email')}"
                    self.results_listbox.insert(tk.END, display_text)
                self.status_var.set(f"Найдено записей: {len(filtered)}")
            else:
                self.results_listbox.insert(tk.END, "Ничего не найдено")
                self.status_var.set("Ничего не найдено")
                
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
            self.status_var.set(f"Ошибка: {str(e)}")
    
    def get_item_details(self, item_id):
        """Получение детальной информации о записи по ID"""
        try:
            url = f"{self.api_base_url}/users/{item_id}"
            return self.make_api_request(url)
        except:
            return {}
    
    def get_selected_item_from_results(self):
        selection = self.results_listbox.curselection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите запись из результатов")
            return None
        
        selected_text = self.results_listbox.get(selection[0])
        if selected_text == "Ничего не найдено":
            return None
        
        # Извлекаем ID (в JSONPlaceholder ID не отображается в тексте, поэтому нужен костыль)
        # Для реального API лучше сохранять ID отдельно.
        # Я для примера сделаю отдельный словарь с данными.
        # В упрощённом варианте: можно при поиске сохранять результаты в атрибут self.last_results
        # и по индексу получать ID. Сделаем так:
        if not hasattr(self, 'last_results') or not self.last_results:
            return None
        if selection[0] < len(self.last_results):
            return self.last_results[selection[0]].get('id')
        return None
    
    # ---------- Добавление в избранное ----------
    def add_to_favorites_from_results(self):
        if not hasattr(self, 'last_results') or not self.last_results:
            messagebox.showwarning("Предупреждение", "Сначала выполните поиск")
            return
        
        selection = self.results_listbox.curselection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите запись")
            return
        
        idx = selection[0]
        if idx >= len(self.last_results):
            return
        
        item = self.last_results[idx]
        item_id = str(item.get('id'))
        
        if item_id in self.favorites:
            messagebox.showinfo("Информация", f"Запись ID {item_id} уже в избранном")
            return
        
        # Детальная информация
        details = self.get_item_details(item_id)
        
        self.favorites[item_id] = {
            'id': item_id,
            'name': details.get('name', ''),
            'username': details.get('username', ''),
            'email': details.get('email', ''),
            'phone': details.get('phone', ''),
            'website': details.get('website', ''),
            'added_at': datetime.now().isoformat()
        }
        self.save_favorites()
        self.status_var.set(f"Запись {details.get('name', item_id)} добавлена в избранное")
        messagebox.showinfo("Успех", "Добавлено в избранное")
    
    def remove_from_favorites(self):
        selection = self.favorites_listbox.curselection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите запись в избранном")
            return
        
        selected_text = self.favorites_listbox.get(selection[0])
        # Извлечение ID из строки (после "[ID: ...]")
        import re
        match = re.search(r'\[ID: (\d+)\]', selected_text)
        if not match:
            return
        item_id = match.group(1)
        
        if messagebox.askyesno("Подтверждение", f"Удалить запись {selected_text} из избранного?"):
            del self.favorites[item_id]
            self.save_favorites()
            self.status_var.set("Запись удалена из избранного")
    
    def view_details_from_results(self):
        if not hasattr(self, 'last_results') or not self.last_results:
            return
        selection = self.results_listbox.curselection()
        if not selection:
            return
        idx = selection[0]
        if idx >= len(self.last_results):
            return
        item = self.last_results[idx]
        self.show_details(item.get('id'))
    
    def view_details_from_favorites(self):
        selection = self.favorites_listbox.curselection()
        if not selection:
            return
        selected_text = self.favorites_listbox.get(selection[0])
        import re
        match = re.search(r'\[ID: (\d+)\]', selected_text)
        if match:
            self.show_details(match.group(1))
    
    def show_details(self, item_id):
        details = self.get_item_details(item_id)
        if not details:
            messagebox.showerror("Ошибка", "Не удалось получить детали")
            return
        
        win = tk.Toplevel(self.root)
        win.title(f"Детали записи #{item_id}")
        win.geometry("450x400")
        
        text = tk.Text(win, wrap=tk.WORD, font=("Arial", 10), padx=10, pady=10)
        text.pack(fill=tk.BOTH, expand=True)
        
        info = f"""
╔════════════════════════════════════════════╗
║            ДЕТАЛЬНАЯ ИНФОРМАЦИЯ            ║
╚════════════════════════════════════════════╝

ID: {details.get('id')}
Имя: {details.get('name', 'Н/Д')}
Username: {details.get('username', 'Н/Д')}
Email: {details.get('email', 'Н/Д')}
Телефон: {details.get('phone', 'Н/Д')}
Вебсайт: {details.get('website', 'Н/Д')}

Адрес:
   Улица: {details.get('address', {}).get('street', '')}
   Город: {details.get('address', {}).get('city', '')}
   ZIP: {details.get('address', {}).get('zipcode', '')}

Компания: {details.get('company', {}).get('name', '')}
"""
        text.insert(tk.END, info)
        text.config(state=tk.DISABLED)
        ttk.Button(win, text="Закрыть", command=win.destroy).pack(pady=10)
    
    def show_favorites(self):
        if not self.favorites:
            messagebox.showinfo("Информация", "Избранное пусто")
            return
        
        fav_window = tk.Toplevel(self.root)
        fav_window.title("Избранные записи")
        fav_window.geometry("600x400")
        
        columns = ('id', 'name', 'email')
        tree = ttk.Treeview(fav_window, columns=columns, show='headings')
        tree.heading('id', text='ID')
        tree.heading('name', text='Имя')
        tree.heading('email', text='Email')
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        for item_id, data in self.favorites.items():
            tree.insert('', tk.END, values=(item_id, data.get('name', ''), data.get('email', '')))
        
        ttk.Button(fav_window, text="Закрыть", command=fav_window.destroy).pack(pady=10)

def main():
    root = tk.Tk()
    app = WebSiteManager(root)
    root.mainloop()

if __name__ == "__main__":
    main()
