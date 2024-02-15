#GUI周辺
import tkinter as tk 
from tkinter import filedialog, messagebox
#優先度
import heapq
#出現回数
from collections import Counter

#デコーダとエンコーダの実装
class HuffmanEncoderDecoder:
    #ウインドウの初期化ってとっても大事(n敗)
    def __init__(self):
        self.root = tk.Tk()#ウインドウを作る
        self.root.title("omg Encoder/Decoder")#タイトル設定
        self.file_path_entry = tk.Entry(self.root, width=50)#幅を設定
        self.file_path_entry.pack(pady=10)
        #ファイルの参照ボタン
        select_file_button = tk.Button(self.root, text="ファイルを参照", command=self.select_file)
        select_file_button.pack(pady=10)
        #エンコード、デコード用のボタン配置
        encode_button = tk.Button(self.root, text="エンコード", command=self.encode_file)
        encode_button.pack(pady=5)
        decode_button = tk.Button(self.root, text="デコード", command=self.decode_file)
        decode_button.pack(pady=5)
        #ファイルパスとログ表示のテキストボックス
        self.selected_file = None
        self.log_text = tk.Text(self.root, height=20, width=70)
        self.log_text.pack(pady=10)
        # ログリストの追加
        self.log_info = []
        #設定終了
        self.root.mainloop()

    def select_file(self):
        #ファイルパスの取得
        self.selected_file = filedialog.askopenfilename(title="ファイルを選択")
        #新しいファイル内容を削除して新しいものを入力
        self.file_path_entry.delete(0, tk.END)
        self.file_path_entry.insert(0, self.selected_file)

    def encode_file(self):
        #ファイルがあったら処理開始
        if self.selected_file:
            #.omgファイルで出力
            output_file_path = self.selected_file + ".omg"
            #ハフマンコードと圧縮データを取得して圧縮する
            huffman_codes, compressed_data = self.compress_file(self.selected_file, output_file_path)
            #ダイアログの表示
            self.show_info_and_log("エンコード完了", "ファイルをエンコードしました。", huffman_codes, compressed_data)

    def decode_file(self):
        #選択したファイルが存在しその拡張子が.omgなら実行
        if self.selected_file and self.selected_file.endswith(".omg"):
            output_file_path = self.selected_file[:-4]  # .omg 拡張子を取り除く
            #ファイルをデコードする
            decoded_text = self.decompress_file(self.selected_file, output_file_path)
            #ログにデコード結果を出力する
            self.log([f"Decoded Text: {decoded_text}"])
            self.show_info_and_log("デコード完了", "ファイルをデコードしました。", decoded_text)

    def compress_file(self, input_file, output_file):
        #入力ファイルの読み込み文字コードはutf-8
        with open(input_file, 'r', encoding='utf-8') as file:
            data = file.read()

        #データからハフマンツリーを作る
        root = self.build_huffman_tree(data)
        #ハフマンコードの取得をする
        huffman_codes = self.get_huffman_codes(root)
        #ハフマンコードを使いデータを圧縮
        compressed_data = self.compress_data(data, huffman_codes)

        #ハフマンコードと圧縮したデータをファイルに書き出す
        with open(output_file, 'w', encoding='utf-8') as file:
            #char型でファイルに書き込み
            for char, code in huffman_codes.items():
                file.write(f"{char}: {code}\n")
            #区切りに改行をぶちこむ
            file.write("\nCompressed Data:\n")
            #ファイルに書き込む
            file.write(compressed_data)

        #ハフマンコードと圧縮データを返す
        return huffman_codes, compressed_data

    def decompress_file(self, input_file, output_file):
        #データを読み込み各行のデータを取得する
        with open(input_file, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        #ファイルから読み取ったハフマンコードと圧縮データを取得
        huffman_codes, compressed_data = self.read_huffman_codes(lines)

        # デバッグログ: huffman_codes の内容
        print("Huffman Codes:", huffman_codes)

        #ハフマンツリー構築
        root = self.build_huffman_tree_from_codes(huffman_codes)
        #テキストを構築したハフマンツリーでデコードする
        decoded_text = self.decompress_data(compressed_data, root)

        #デコード結果をファイルに書き込む
        with open(output_file, 'w', encoding='utf-8') as file:
            file.write(decoded_text)

        #デコード結果を返す
        return decoded_text

    def read_huffman_codes(self, lines):
        #辞書と文字列の初期化
        huffman_codes = {}
        compressed_data = ""
        #読み取り中フラグの初期化
        reading_compressed_data = False

        #各行へ処理をあてる
        for line in lines:
            #読み取り中ではない場合
            if not reading_compressed_data:
                #空行があったら読み取り開始
                if line.strip() == "":
                    reading_compressed_data = True
                else:
                    #対応する文字とコードを抽出し辞書へ
                    char, code = line.strip().split(': ')
                    huffman_codes[code] = char
            #読み取り中ならば
            elif reading_compressed_data:
                #行から圧縮データを抽出し文字列へ
                compressed_data += line.strip()
    
        #読み取ったコードとデータを返す
        return huffman_codes, compressed_data

    def build_huffman_tree(self, data):
        #データの出現頻度計算
        frequency = Counter(data)
        #出現頻度と文字でノード生成　優先度付きのキューへ格納する
        heap = [Node(char, freq) for char, freq in frequency.items()]
        heapq.heapify(heap)

        while len(heap) > 1:
            #ヒープから最小2つのノードを取り出す
            left = heapq.heappop(heap)
            right = heapq.heappop(heap)

            #取り出したノードを結合し新しくノードを作る
            merged_node = Node(data='$', frequency=left.frequency + right.frequency)
            merged_node.left = left
            merged_node.right = right

            #新しいノードをヒープへぶち込む
            heapq.heappush(heap, merged_node)

        #ヒープを返す
        return heap[0]

    def build_huffman_tree_from_codes(self, huffman_codes):
        #ハフマンツリーのルートノードを作成する
        root = Node('$', 0)
        #ハフマンコードの項目にノードを挿入
        for code, char in huffman_codes.items():
            self.insert_node(root, code, char)

        # 新しいログリストを追加
        log_info = [f"Items for building Huffman tree: {huffman_codes.items()}",
                    f"Heap after building Huffman tree: {[node.data for node in self.traverse_tree(root)]}"]
        self.log(log_info)

        #rootを返す
        return root

    def get_huffman_codes(self, root, code="", mapping=None):
        #ハフマンツリーを走査してノードに対するコードを取得
        if mapping is None:
            mapping = {}
        if root:
            #葉に到達したらノードデータとコードをマッピングする
            if root.left is None and root.right is None:
                mapping[root.data] = code
            #左子ノードに0を追加して再帰呼び出し
            mapping.update(self.get_huffman_codes(root.left, code + "0", mapping))
            #右子ノードに1を追加して再帰呼び出し
            mapping.update(self.get_huffman_codes(root.right, code + "1", mapping))
        return mapping

    def compress_data(self, data, mapping):
        #コードをもとに圧縮
        compressed_data = "".join(mapping[char] for char in data)
        return compressed_data

    def decompress_data(self, compressed_data, root):
        #圧縮データをもとにハフマンツリーを走査しデータの復元をする
        current_node = root
        decoded_text = []

        #ビットごとに処理をする
        for bit in compressed_data:
            #0なら左子ノードへ
            if bit == "0":
                current_node = current_node.left
            #1なら右子ノード
            elif bit == "1":
                current_node = current_node.right

            #葉ノードに到達したらノードのデータをもとに復元リストに追加してrootへ戻る
            if current_node.left is None and current_node.right is None:
                decoded_text.append(current_node.data)
                current_node = root
        #復元後のデータを文字列に結合して返す
        return ''.join(decoded_text)

    def log(self, log_info):
        # 新しいログリストを追加
        self.log_info.extend(log_info)
        #ログ情報を表示
        self.log_text.delete("1.0", tk.END)
        self.log_text.insert(tk.END, "\n".join(map(str, self.log_info)))

    def show_info_and_log(self, title, info, *log_info):
        #ログをダイアログへ書き込みファイルもついでに出力しておく
        formatted_log_info = [info] + [str(item) for item in log_info]
        messagebox.showinfo(title, info)
        self.log(formatted_log_info)
        self.export_log_to_file()

    def export_log_to_file(self):
        #ログ出力
        log_content = "\n".join(map(str, self.log_info))
        with open("log.txt", "w") as log_file:
            log_file.write(log_content)

    def insert_node(self, root, code, char):
        #ハフマンツリーにノードをぶちこむ
        node = Node(char, 0)
        current = root

        for bit in code:
            #0なら左子ノードへ移動存在しないならノード作成
            if bit == '0':
                if not current.left:
                    current.left = Node('$', 0)
                current = current.left
            #1なら右子ノードへ移動存在しないならノード作成
            elif bit == '1':
                if not current.right:
                    current.right = Node('$', 0)
                current = current.right

        #ノードにデータ設定
        current.data = char

    def traverse_tree(self, root):
        #ツリーを深さ優先で走査、ノード収集
        result = []
        if root:
            #左部分木を走査
            result.extend(self.traverse_tree(root.left))
            #現在ノードをリストへ
            result.append(root)
            #右部分木を走査
            result.extend(self.traverse_tree(root.right))
        return result

#ハフマンツリーのノード
class Node:
    def __init__(self, data, frequency):
        #データと出現頻度初期化
        self.data = data
        self.frequency = frequency
        #左右の子ノードの初期化
        self.left = None
        self.right = None

    def __lt__(self, other):
        #ノード動詞の頻度比較
        return self.frequency < other.frequency

if __name__ == "__main__":
    app = HuffmanEncoderDecoder()