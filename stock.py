import tkinter as tk
from tkinter import ttk, messagebox
import random
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# 한글 폰트 설정
plt.rc('font', family='Malgun Gothic')

class StockTradingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("가상 주식 투자 게임")
        self.root.geometry("1200x800")
        
        # 초기 자본 (예: 1000만 원)
        self.balance = 10000000
        
        # 생활비 (매일 3만 원 차감)
        self.daily_expense = 30000
        
        # 기존 주식 목록 (가격은 업종별로 다르게 설정, 기존보다 낮게 설정)
        self.stocks = {
            "아오전자": random.randint(20000, 40000),  # 전자
            "HO 그룹": random.randint(25000, 35000),   # 금융
            "동방제약": random.randint(15000, 35000),   # 제약
            "SM하이닉스": random.randint(20000, 30000), # 반도체
            "고려조선": random.randint(18000, 28000),   # 조선
            "CCH": random.randint(15000, 25000),        # 화학
            "빅브라더": random.randint(22000, 32000),    # IT
            "솔라에너지": random.randint(12000, 22000)    # 에너지
        }
        # 주식의 업종
        self.stock_industry = {
            "아오전자": "전자",
            "HO 그룹": "금융",
            "동방제약": "제약",
            "SM하이닉스": "반도체",
            "고려조선": "조선",
            "CCH": "화학",
            "빅브라더": "IT",
            "솔라에너지": "에너지"
        }
        # 주식별 과거 가격 기록 (최근 100일)
        self.stock_history = {stock: [price] for stock, price in self.stocks.items()}
        # 보유 주식 수, 매수 가격 기록
        self.owned_stocks = {stock: 0 for stock in self.stocks}
        self.buy_prices = {stock: [] for stock in self.stocks}
        # 평상시 주가 변화 경향 (일일 변동량은 ±50 원 정도)
        self.trend = {stock: random.randint(-50, 50) for stock in self.stocks}
        # 주가가 1000원 이하로 유지된 연속 일수
        self.low_price_days = {stock: 0 for stock in self.stocks}
        # 사이드카 발동: 해당 주식은 5일간 가격 변동 정지
        self.sidecar = {stock: 0 for stock in self.stocks}
        # 업종 리스트 (뉴스 이벤트 시 활용)
        self.industries = ["전자", "자동차", "제약", "반도체", "조선", "화학", "에너지", "유통", "금융", "IT"]
        # 신규 기업 이름 리스트 (편집 가능)
        self.new_company_names = ["뉴텍", "비전솔루션","스타크인더스트리","글로벌파트너스", "이노베이션", "테크스타","주혁컴퍼니","동수 그룹","한솔하이","마이크로하드","앤갈릭스","로봇록스"]
        # 그래프 옵션: 체크박스로 그래프에 표시할 회사를 선택
        self.graph_vars = {}
        # 호재/악재 영향 기간 (5일)
        self.news_effect_duration = {stock: 0 for stock in self.stocks}
        self.news_effect = {stock: 0 for stock in self.stocks}  # 0: 영향 없음, 1: 호재, -1: 악재
        # 뉴스 지연 적용 (3일 뒤에 적용)
        self.news_delay = {stock: 0 for stock in self.stocks}
        # 뉴스 데이터 로드
        self.news_data = self.load_news_data("news.txt")
        
        # 전체 마켓 이벤트 (전체 시장에 영향을 주는 뉴스)
        self.global_news_active = False
        self.global_news_effect = 0  # 0: 영향 없음, 1: 호재, -1: 악재
        self.global_news_duration = 0
        
        # 글로벌 이벤트 뉴스 리스트 추가
        self.global_news = {
            "호재": [
                "국제 금리 인하 예상으로 증시 호조",
                "경기 회복 기대감 확산",
                "미국과 무역 협정 체결",
                "국내 경제성장률 상향 조정",
                "정부 경기부양책 발표"
            ],
            "악재": [
                "국제 금리 인상 우려로 증시 하락",
                "경제 침체 우려 확산",
                "트럼프, 세계무역전쟁 선포",
                "국내 경제성장률 하향 조정",
                "대규모 기업 스캔들 발생"
            ]
        }
        
        # 레이아웃: 상단은 매수/매도 화면, 하단은 그래프 영역(왼쪽: 그래프, 오른쪽: 옵션)
        self.top_frame = tk.Frame(self.root)
        self.top_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=False)
        self.bottom_frame = tk.Frame(self.root)
        self.bottom_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        
        self.create_widgets()
        self.update_stock_prices()  # 1초마다 하루 업데이트
        self.schedule_news_event()  # 뉴스 이벤트 예약
        self.schedule_global_event()  # 글로벌 이벤트 예약
        
    def load_news_data(self, filename):
        # 뉴스 데이터를 파일에서 로드
        news_data = {}
        try:
            with open(filename, "r", encoding="utf-8") as file:
                for line in file:
                    industry, news_type, content = line.strip().split(",")
                    if industry not in news_data:
                        news_data[industry] = {"호재": [], "악재": []}
                    news_data[industry][news_type].append(content)
        except FileNotFoundError:
            # 파일이 없을 경우 기본 데이터 생성
            for industry in self.industries:
                news_data[industry] = {
                    "호재": [f"{industry} 업종 호재 뉴스"],
                    "악재": [f"{industry} 업종 악재 뉴스"]
                }
            messagebox.showwarning("파일 없음", "news.txt 파일을 찾을 수 없습니다. 기본 뉴스를 사용합니다.")
        return news_data
    
    def create_widgets(self):
        # 상단 프레임: 잔고, 주식 테이블, 매수/매도 컨트롤, 뉴스
        self.balance_label = tk.Label(self.top_frame, text=f"잔고: {self.balance:,}원", font=("Arial", 14))
        self.balance_label.pack(pady=5)
        
        self.stock_frame = tk.Frame(self.top_frame)
        self.stock_frame.pack()
        self.tree = ttk.Treeview(self.stock_frame, columns=("이름", "업종", "가격", "보유 수량", "수익률"), show='headings')
        self.tree.heading("이름", text="주식 이름")
        self.tree.heading("업종", text="업종")
        self.tree.heading("가격", text="현재 가격")
        self.tree.heading("보유 수량", text="보유 수량")
        self.tree.heading("수익률", text="수익률 (%)")
        self.tree.pack(padx=5, pady=5)
        
        self.control_frame = tk.Frame(self.top_frame)
        self.control_frame.pack(pady=5)
        self.stock_var = tk.StringVar()
        self.stock_menu = ttk.Combobox(self.control_frame, textvariable=self.stock_var, values=list(self.stocks.keys()))
        self.stock_menu.pack(side=tk.LEFT, padx=5)
        self.amount_entry = tk.Entry(self.control_frame)
        self.amount_entry.pack(side=tk.LEFT, padx=5)
        self.buy_button = tk.Button(self.control_frame, text="매수", command=self.buy_stock)
        self.buy_button.pack(side=tk.LEFT, padx=5)
        self.sell_button = tk.Button(self.control_frame, text="매도", command=self.sell_stock)
        self.sell_button.pack(side=tk.LEFT, padx=5)
        
        self.news_label = tk.Label(self.top_frame, text="", font=("Arial", 12), fg="red")
        self.news_label.pack(pady=5)
        
        # 글로벌 뉴스 레이블 추가 (글로벌 이벤트를 표시하기 위한 레이블)
        self.global_news_label = tk.Label(self.top_frame, text="", font=("Arial", 12, "bold"), fg="blue")
        self.global_news_label.pack(pady=5)
        
        self.update_stock_table()
        
        # 하단 프레임: 그래프 영역과 그래프 옵션 영역(오른쪽에 배치)
        self.graph_container = tk.Frame(self.bottom_frame)
        self.graph_container.pack(fill=tk.BOTH, expand=True)
        # 그래프 프레임 (왼쪽)
        self.graph_frame = tk.Frame(self.graph_container)
        self.graph_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.figure, self.ax = plt.subplots(figsize=(10, 6))
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.graph_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        # 그래프 옵션 프레임 (오른쪽)
        self.options_frame = tk.Frame(self.graph_container)
        self.options_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=5)
        tk.Label(self.options_frame, text="그래프에 표시할 주식 선택").pack(anchor="n")
        self.update_graph_options()
        
        self.plot_button = tk.Button(self.bottom_frame, text="그래프 업데이트", command=self.plot_stock_prices)
        self.plot_button.pack(pady=5)
    
    def update_graph_options(self):
        # 그래프 옵션 프레임 내의 기존 체크박스 삭제
        for widget in self.options_frame.winfo_children():
            if isinstance(widget, tk.Checkbutton):
                widget.destroy()
        self.graph_vars = {}
        for stock in self.stocks:
            var = tk.BooleanVar(value=True)
            chk = tk.Checkbutton(self.options_frame, text=stock, variable=var)
            chk.pack(anchor="w")
            self.graph_vars[stock] = var
    
    def update_stock_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        # 주식을 가격순(내림차순)으로 정렬하여 표시
        for stock, price in sorted(self.stocks.items(), key=lambda x: x[1], reverse=True):
            profit_rate = "-"
            if self.owned_stocks[stock] > 0 and self.buy_prices[stock]:
                avg_price = sum(self.buy_prices[stock]) / len(self.buy_prices[stock])
                profit_rate = f"{((price - avg_price) / avg_price) * 100:.2f}%"
            self.tree.insert("", "end", values=(
                stock, 
                self.stock_industry[stock], 
                f"{int(price):,}", 
                self.owned_stocks[stock], 
                profit_rate
            ))
        # 콤보박스 업데이트: 신규 기업이 추가되면 목록에 반영
        self.stock_menu['values'] = list(self.stocks.keys())
        # options_frame이 생성된 경우에만 그래프 옵션 업데이트
        if hasattr(self, 'options_frame'):
            self.update_graph_options()
    
    def plot_stock_prices(self):
        self.ax.clear()
        # 그래프는 선택한 주식들의 최근 100일 가격을 표시
        for stock, var in self.graph_vars.items():
            if var.get() and stock in self.stock_history:
                history = self.stock_history[stock][-100:]
                self.ax.plot(range(len(history)), history, label=stock)
        self.ax.set_title("주식 가격 변동 (최근 100일)")
        self.ax.legend(loc='upper right')
        self.canvas.draw()
    
    def schedule_news_event(self):
        # 5~10일(초) 간격으로 뉴스 이벤트 발생
        interval = random.randint(5, 10) * 3000
        self.root.after(interval, self.generate_news)
    
    def schedule_global_event(self):
        # 30~60일(초) 간격으로 글로벌 이벤트 발생
        interval = random.randint(30, 60) * 3000
        self.root.after(interval, self.generate_global_event)
    
    def generate_global_event(self):
        # 글로벌 이벤트 생성 (전체 시장에 영향)
        if not self.global_news_active:
            # 호재 또는 악재 선택
            news_type = random.choice(["호재", "악재"])
            news_content = random.choice(self.global_news[news_type])
            
            # 효과 설정 (1: 호재, -1: 악재)
            self.global_news_effect = 1 if news_type == "호재" else -1
            # 효과 지속 기간 (7-10일)
            self.global_news_duration = random.randint(7, 10)
            self.global_news_active = True
            
            # 글로벌 뉴스 표시
            color = "blue" if news_type == "호재" else "red"
            self.global_news_label.config(text=f"[전체 시장 {news_type}] {news_content}", fg=color)
            
            # 효과 강도 설정 (일별 변동에 추가될 값)
            self.global_effect_intensity = random.randint(200, 500) * self.global_news_effect
        
        # 다음 글로벌 이벤트 예약
        self.schedule_global_event()
    
    def generate_news(self):
        # 업종 선택
        industry = random.choice(list(self.news_data.keys()))
        # 호재 또는 악재 선택
        news_type = random.choice(["호재", "악재"])
        news_content = random.choice(self.news_data[industry][news_type])
        # 내부적으로 효과를 결정 (1: 호재, -1: 악재)
        news_effect = 1 if news_type == "호재" else -1
        # 해당 업종의 주식에 효과 적용 (3일 뒤에 적용)
        for stock, ind in self.stock_industry.items():
            if ind == industry:
                self.news_delay[stock] = 3  # 3일 뒤에 적용
                self.news_effect[stock] = news_effect
                self.news_effect_duration[stock] = 5  # 5일 동안 효과 지속
        # 뉴스 표시
        final_news = f"뉴스) {industry} 업종: {news_content}"
        self.news_label.config(text=final_news)
        self.schedule_news_event()
    
    def update_stock_prices(self):
        # 생활비 차감
        self.balance -= self.daily_expense
        if self.balance < 0:
            messagebox.showinfo("게임 오버", "생활비를 낼 돈이 없습니다. 게임이 종료됩니다.")
            self.root.quit()
            return
        self.balance_label.config(text=f"잔고: {self.balance:,}원")
        
        # 글로벌 이벤트 효과 적용
        if self.global_news_active:
            if self.global_news_duration > 0:
                self.global_news_duration -= 1
            else:
                self.global_news_active = False
                self.global_news_effect = 0
                self.global_news_label.config(text="")
        
        for stock in list(self.stocks.keys()):
            # 뉴스 지연 적용
            if self.news_delay[stock] > 0:
                self.news_delay[stock] -= 1
            elif self.news_effect_duration[stock] > 0:
                # 호재/악재 효과 적용
                self.trend[stock] += self.news_effect[stock] * random.randint(100, 300)
                self.news_effect_duration[stock] -= 1
            else:
                self.news_effect[stock] = 0  # 효과 종료
            
            # 글로벌 이벤트 효과 추가
            if self.global_news_active:
                # 글로벌 이벤트는 모든 주식에 영향을 미침 (업종별로 영향도가 약간 다름)
                industry_factor = 0.7 + (0.6 * random.random())  # 0.7 ~ 1.3 사이의 랜덤 계수
                global_effect = int(self.global_effect_intensity * industry_factor)
                self.trend[stock] += global_effect
            
            # 경향성 조정: 지나치게 +이거나 -이면 반대 부호로 조정
            if self.trend[stock] > 500:
                self.trend[stock] = -300
            elif self.trend[stock] < -500:
                self.trend[stock] = 300
            
            # 일반적인 주가 변동
            self.trend[stock] += random.randint(-50, 50)
            self.trend[stock] = max(-500, min(500, self.trend[stock]))
            self.stocks[stock] += self.trend[stock]
            self.stocks[stock] = max(100, int(self.stocks[stock]))  # 최소 가격 100원 설정
            
            # 주식 가격이 1000원 이하이면 연속일수 증가, 아니면 초기화
            if self.stocks[stock] <= 1000:
                self.low_price_days[stock] += 1
            else:
                self.low_price_days[stock] = 0
            
            # 5일 이상 1000원 이하이면 상장폐지
            if self.low_price_days[stock] >= 5:
                self.delist_stock(stock)
                continue
            
            # 가격 변동 기록 (최근 100일)
            self.stock_history[stock].append(self.stocks[stock])
            if len(self.stock_history[stock]) > 100:
                self.stock_history[stock].pop(0)
        
        self.update_stock_table()
        self.plot_stock_prices()  # 그래프 갱신
        self.root.after(3000, self.update_stock_prices)
    
    def delist_stock(self, stock):
        # 상장폐지: 해당 주식 제거 후 신규 기업 추가
        del self.stocks[stock]
        del self.stock_industry[stock]
        del self.stock_history[stock]
        del self.owned_stocks[stock]
        del self.buy_prices[stock]
        del self.trend[stock]
        del self.low_price_days[stock]
        del self.sidecar[stock]
        del self.news_effect[stock]
        del self.news_effect_duration[stock]
        del self.news_delay[stock]
        messagebox.showinfo("상장폐지", f"{stock} 상장폐지됨!")
        # 신규 기업 추가 (신규 기업 이름 리스트에서 할당)
        if self.new_company_names:
            new_stock = self.new_company_names.pop(0)
        else:
            new_stock = "신규기업" + str(random.randint(1, 100))
        # 시작 가격도 낮게 설정
        new_price = random.randint(5000, 20000)
        new_industry = random.choice(self.industries)
        self.stocks[new_stock] = new_price
        self.stock_industry[new_stock] = new_industry
        self.stock_history[new_stock] = [new_price]
        self.owned_stocks[new_stock] = 0
        self.buy_prices[new_stock] = []
        self.trend[new_stock] = random.randint(-50, 50)
        self.low_price_days[new_stock] = 0
        self.sidecar[new_stock] = 0
        self.news_effect[new_stock] = 0
        self.news_effect_duration[new_stock] = 0
        self.news_delay[new_stock] = 0
        messagebox.showinfo("신규 상장", f"{new_stock} ({new_industry}) 신규 상장됨!")
        self.update_stock_table()
    
    def buy_stock(self):
        # 매수 기능 구현
        stock = self.stock_var.get()
        try:
            amount = int(self.amount_entry.get())
        except ValueError:
            messagebox.showerror("입력 오류", "올바른 숫자를 입력하세요.")
            return
        
        if stock not in self.stocks:
            messagebox.showerror("오류", "존재하지 않는 주식입니다.")
            return
        
        if amount <= 0:
            messagebox.showerror("입력 오류", "양수를 입력하세요.")
            return
        
        # 총 매수 금액 계산
        total_cost = self.stocks[stock] * amount
        
        # 잔고 확인
        if total_cost > self.balance:
            messagebox.showerror("잔고 부족", "주식을 매수할 충분한 자금이 없습니다.")
            return
        
        # 매수 실행
        self.balance -= total_cost
        self.owned_stocks[stock] += amount
        # 매수 가격 기록 (각 주식의 매수 가격을 별도로 기록)
        for _ in range(amount):
            self.buy_prices[stock].append(self.stocks[stock])
        
        # 화면 업데이트
        self.balance_label.config(text=f"잔고: {self.balance:,}원")
        self.update_stock_table()
        
        # 입력 필드 초기화
        self.amount_entry.delete(0, tk.END)
        messagebox.showinfo("매수 완료", f"{stock} {amount}주 매수 완료")

    def sell_stock(self):
        # 매도 기능 구현
        stock = self.stock_var.get()
        try:
            amount = int(self.amount_entry.get())
        except ValueError:
            messagebox.showerror("입력 오류", "올바른 숫자를 입력하세요.")
            return
        
        if stock not in self.stocks:
            messagebox.showerror("오류", "존재하지 않는 주식입니다.")
            return
        
        if amount <= 0:
            messagebox.showerror("입력 오류", "양수를 입력하세요.")
            return
        
        # 보유 주식 확인
        if amount > self.owned_stocks[stock]:
            messagebox.showerror("주식 부족", f"보유한 {stock} 주식이 부족합니다. 현재 {self.owned_stocks[stock]}주 보유 중")
            return
        
        # 매도 실행
        total_sale = self.stocks[stock] * amount
        self.balance += total_sale
        self.owned_stocks[stock] -= amount
        
        # 매수 가격 기록 삭제 (FIFO: 먼저 매수한 것을 먼저 매도)
        for _ in range(amount):
            if self.buy_prices[stock]:
                self.buy_prices[stock].pop(0)
        
        # 화면 업데이트
        self.balance_label.config(text=f"잔고: {self.balance:,}원")
        self.update_stock_table()
        
        # 입력 필드 초기화
        self.amount_entry.delete(0, tk.END)
        messagebox.showinfo("매도 완료", f"{stock} {amount}주 매도 완료 (수익: {total_sale:,}원)")

# 메인 함수 - 애플리케이션 실행
def main():
    root = tk.Tk()
    app = StockTradingApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
