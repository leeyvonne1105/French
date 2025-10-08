import random
import re
from typing import List, Dict, Set, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
#一個字裡只有一個變音母音
#有特定的onset, vowel clusters (如果選到該syllable structure優先選這些cluster)
#設定只有特定子音出現在coda position
#兩個同樣的母音中間要放一個子音
#定冠詞
#le/la 碰到下個字的開頭是母音要變l'
#否定的話前面+ne 後面+pas

@dataclass
class PhonologySystem:
    """音韻系統"""
    consonants: Set[str] = field(default_factory=lambda: {'b','c','d','f','g','h','l','m','n','p','q','r','s','t','v','x','z'})
    vowels: Set[str] = field(default_factory=lambda: {'a', 'e', 'i', 'o', 'u', 'à','é','ê'})
    syllable_patterns: List[str] = field(default_factory=lambda: ['CV','CV','VC','CVC','CVC','CCV','CVV','V'])
    phonotactic_rules: List[str] = field(default_factory=list)
    coda_restrictions: Set[str] = field(default_factory=set)  # 存放不允許在音節尾的子音
    onset_cluster_restrictions:  List[str] = field(default_factory=list)
    vowel_clusters: Set[str] = field(default_factory=set)


    
    def generate_word(self, syllable_count: int = None) -> str:
        if syllable_count is None:
            syllable_count = random.randint(1, 3)

        accented_vowels = {'à','è','ù','é','ê'}
        used_accented = False  # 整個詞中是否已出現變音母音

        word = ""
        for _ in range(syllable_count):
            pattern = random.choice(self.syllable_patterns)
            syllable = ""
            last_vowel = None
            i = 0

            while i < len(pattern):
                char = pattern[i]
                is_last_char = (i == len(pattern) - 1)

                if char == 'C':
                    if i == 0 and len(pattern) > 1 and pattern[i+1] == 'C' and hasattr(self, 'onset_clusters') and self.onset_clusters:
                        cluster = random.choice(list(self.onset_clusters))
                        syllable += cluster
                        i += len(cluster)
                        continue

                    if is_last_char and self.coda_restrictions:
                        consonant = random.choice(list(self.coda_restrictions))
                    else:
                        consonant = random.choice(list(self.consonants))
                    syllable += consonant
                    i += 1

                elif char == 'V':
                    # 如果是連續 VV 結構，而且有 vowel_clusters
                    if i < len(pattern) - 1 and pattern[i + 1] == 'V' and self.vowel_clusters:
                        cluster = random.choice(list(self.vowel_clusters))

                        # 避免含有多個變音母音
                        if any(c in accented_vowels for c in cluster):
                            if used_accented:
                                # 避免使用含變音母音的 cluster
                                possible_clusters = [vc for vc in self.vowel_clusters if not any(c in accented_vowels for c in vc)]
                                if possible_clusters:
                                    cluster = random.choice(possible_clusters)
                                else:
                                    # fallback: 選兩個不重複的普通母音
                                    cluster = ''.join(random.sample(list(self.vowels - accented_vowels), 2))
                            else:
                                used_accented = True

                        syllable += cluster
                        i += 2  # 跳過 VV
                    else:
                        vowel = random.choice(list(self.vowels))
                        while vowel == last_vowel or (vowel in accented_vowels and used_accented):
                            vowel = random.choice(list(self.vowels))

                        if vowel in accented_vowels:
                            used_accented = True

                        syllable += vowel
                        last_vowel = vowel
                        i += 1

            # 處理母音連續時插入子音
            if word and word[-1] in self.vowels and syllable[0] in self.vowels:
                possible_consonants = list(self.coda_restrictions) if self.coda_restrictions else list(self.consonants)
                syllable = random.choice(possible_consonants) + syllable

            word += syllable

        return word

        


    def set_onset_clusters(self):
        """
        設定常見音節開頭叢集
        使用者可以輸入多個子音叢集，例如 "tr", "pl", "st"
        直接按 Enter 結束輸入
        """
        self.onset_clusters = set()  # 初始化
        print("請輸入出現在音節頭的子音們（直接按 Enter 結束）")
        
        while True:
            cluster = input("子音叢集: ").strip()
            if cluster == '':
                break
            # 驗證輸入是否都在子音系統中
            if all(c in self.consonants for c in cluster) and len(cluster) >= 2:
                self.onset_clusters.add(cluster)
                print(f"已添加叢集：{cluster}")
            else:
                print(f"{cluster} 不合法（需至少兩個合法子音）")

    
    def set_coda_restrictions(self):
        """設定允許出現在音節尾的子音（直接按 Enter 結束）"""
        self.coda_restrictions.clear()  # 先清空原本的限制
        print("請輸入出現在音節尾的子音（直接按 Enter 結束）")
        while True:
            c = input("子音: ").strip()
            if c == '':  # 空白鍵結束
                break
            if c in self.consonants:
                self.coda_restrictions.add(c)
                print(f"已添加可出現在音節尾的子音：{c}")
            else:
                print(f"{c} 不在子音系統中")

        if not self.coda_restrictions:
            # 如果沒有輸入任何音節尾子音，預設全部子音都可
            self.coda_restrictions = self.consonants.copy()
            print("未設定任何音節尾子音，預設所有子音都可出現在音節尾。")

    def set_vowel_clusters(self):
        """
        設定常見母音叢集（例如 ai, ou, eau）
        使用者可以輸入多個母音叢集，例如 "ai", "ou", "ie"
        直接按 Enter 結束輸入
        """
        self.vowel_clusters = set()  # 初始化
        print("請輸入出現在詞中常見的母音叢集（直接按 Enter 結束）")
        
        while True:
            cluster = input("母音叢集: ").strip()
            if cluster == '':
                break
            # 驗證輸入是否都是合法母音，且長度 >= 2
            if all(c in self.vowels for c in cluster) and len(cluster) >= 2:
                self.vowel_clusters.add(cluster)
                print(f"✅ 已添加母音叢集：{cluster}")
            else:
                print(f"❌ {cluster} 不合法（需至少兩個合法母音）")



@dataclass
class MorphologyRule:
    """構詞規則"""
    name: str
    rule_type: str  # prefix, suffix, infix, reduplication
    marker: str
    meaning: str
    position: str = ""

@dataclass
class MorphologySystem:
    """構詞系統"""
    rules: List[MorphologyRule] = field(default_factory=list)
    word_classes: Dict[str, List[str]] = field(default_factory=lambda: {
        'noun': [], 'verb': [], 'adjective': []#, 'adverb': []
    })

    def add_rule(self, name: str, rule_type: str, marker: str, meaning: str):
        """添加構詞規則"""
        rule = MorphologyRule(name, rule_type, marker, meaning)
        self.rules.append(rule)
    
    def apply_rules(self, word: str, word_class: str) -> str:
        """依據詞類套用規則"""
        for rule in self.rules:
    
            # 複數（只套用在名詞）
            if rule.name == "plural" and word_class == "noun":
                word = word + rule.marker

            # 否定（只套用在動詞）
            elif rule.name == "negative" and word_class == "verb":
                prefix, suffix = rule.marker  # 例如 ("ne ", " pas")
                word = prefix + word + suffix

        return word

    def apply_morphology(self, base_word: str, rule_name: str) -> str:
        """應用構詞規則"""
        for rule in self.rules:
            if rule.name == rule_name:
                if rule.rule_type == 'prefix':
                    return rule.marker + base_word
                elif rule.rule_type == 'suffix':
                    return base_word + rule.marker
                elif rule.rule_type == 'reduplication':
                    return base_word + base_word
        return base_word

@dataclass
class SyntaxRule:
    """句法規則"""
    name: str
    pattern: str  # SVO, SOV, VSO etc.
    description: str

@dataclass
class SyntaxSystem:
    """句法系統"""
    word_order: str = "SVO"
    rules: List[SyntaxRule] = field(default_factory=list)

    def add_rule(self, name: str, pattern: str, description: str):
        """添加句法規則"""
        rule = SyntaxRule(name, pattern, description)
        self.rules.append(rule)

    def generate_sentence(self, subject: str, verb: str, obj: str = "") -> str:
        """根據語序生成句子"""
        if self.word_order == "SVO":
            return f"{subject} {verb} {obj}".strip()
        elif self.word_order == "SOV":
            return f"{subject} {obj} {verb}".strip()
        elif self.word_order == "VSO":
            return f"{verb} {subject} {obj}".strip()
        else:
            return f"{subject} {verb} {obj}".strip()

class LanguageCreatorGame:
    """語言創造者遊戲主類"""

    def __init__(self):
        self.phonology = PhonologySystem()
        self.morphology = MorphologySystem()
        self.syntax = SyntaxSystem()
        self.vocabulary = defaultdict(list)  # {詞性: [詞語列表]}
        self.current_level = 1


    def display_welcome(self):
        """顯示歡迎訊息"""
        print("=" * 60)
        print("🌍 歡迎來到語言創造者遊戲！ 🌍")
        print("=" * 60)
        print("你將通過三個層次來創造一個全新的語言：")
        print("第一層：音韻系統 (Phonology)")
        print("第二層：構詞系統 (Morphology)")
        print("第三層：句法系統 (Syntax)")
        print("=" * 60)

    def level_1_phonology(self):
        """第一關：設定音韻系統"""
        print("\n🔤 第一關：音韻系統設定")
        print("-" * 40)
        print("讓我們為你的語言設定基本的聲音系統！")

        # 設定子音
        #print(f"\n目前的子音：{', '.join(sorted(self.phonology.consonants))}")
        while True:
            print(f"\n目前的子音：{', '.join(sorted(self.phonology.consonants))}")
            choice = input("\n你想要 (a)添加子音 (b)移除子音 (c)繼續下一步？ ").lower()
            if choice == 'a':
                new_consonant = input("請輸入要添加的子音：")
                if new_consonant and len(new_consonant) <= 2:
                    self.phonology.consonants.add(new_consonant)
                    print(f"已添加子音：{new_consonant}")
            elif choice == 'b':
                remove_consonant = input("請輸入要移除的子音：")
                if remove_consonant in self.phonology.consonants:
                    self.phonology.consonants.remove(remove_consonant)
                    print(f"已移除子音：{remove_consonant}")
            elif choice == 'c':
                break


        # 設定母音
        #print(f"\n目前的母音：{', '.join(sorted(self.phonology.vowels))}")
        while True:
            print(f"\n目前的母音：{', '.join(sorted(self.phonology.vowels))}")
            choice = input("\n你想要 (a)添加母音 (b)移除母音 (c)繼續下一步？ ").lower()

            if choice == 'a':
                new_vowel = input("請輸入要添加的母音：")
                if new_vowel and len(new_vowel) <= 3:
                    self.phonology.vowels.add(new_vowel)
                    print(f"已添加母音：{new_vowel}")

            elif choice == 'b':
                remove_vowel = input("請輸入要移除的母音：")
                if remove_vowel in self.phonology.vowels:
                    self.phonology.vowels.remove(remove_vowel)
                    print(f"已移除母音：{remove_vowel}")
            elif choice == 'c':
                break

        # 設定音節結構
        print(f"\n目前的詞彙音節結構：{', '.join(self.phonology.syllable_patterns)}")
        print("(C=子音, V=母音)")


        self.phonology.set_coda_restrictions()
        self.phonology.set_onset_clusters()
        self.phonology.set_vowel_clusters()

        # 生成範例詞語
        print("\n🎲 讓我們用你的音韻系統生成一些詞語：")
        for i in range(5):
            word = self.phonology.generate_word()
            print(f"{i+1}. {word}")
            self.vocabulary['unknown'].append(word)
            
                    
        print(f"\n✅ 第一關完成！")
        self.current_level = 2

    def apply_def_article(self, word: str) -> str:
            """加入定冠詞，若遇到母音開頭詞則改成 l' 形式"""
            def_article_rules = [r for r in self.morphology.rules if r.name == "definite_article"]

            if not def_article_rules:
                return word  # 沒有定冠詞設定

            chosen_rule = random.choice(def_article_rules)
            marker = chosen_rule.marker.strip()  # 例如 "le", "la"
            first_letter = word[0]

            # 如果冠詞是 le/la 且詞以母音開頭 → 用 l'
            if marker in {"le", "la"} and first_letter in self.phonology.vowels:
                return f"l'{word}"
            else:
                return f"{marker} {word}"


    def level_2_morphology(self):
       

        """第二關：設定構詞系統"""
        print("\n🔧 第二關：構詞系統設定")
        print("-" * 40)
        print("現在我們來為語言添加構詞規則！")

        # 將之前生成的詞語分類
        print("\n首先，讓我們為之前生成的詞語分類：")
        for word in self.vocabulary['unknown'][:]:
            print(f"\n詞語：{word}")
            word_class = input("這個詞是 (n)名詞 (v)動詞 (a)形容詞").lower()

            if word_class == 'n':
                self.vocabulary['noun'].append(word)
            elif word_class == 'v':
                self.vocabulary['verb'].append(word)
            elif word_class == 'a':
                self.vocabulary['adjective'].append(word)
            else:
                self.vocabulary['noun'].append(word)  # 預設為名詞

            self.vocabulary['unknown'].remove(word)

        # 添加構詞規則
        print("\n現在我們來創建構詞規則：")

        # 複數規則
        plural_marker = input("請設定複數標記（例如：-s, -en, -i）：") or "-i"
        self.morphology.add_rule("plural", "suffix", plural_marker, "複數")
        print(f"已添加複數規則：詞根 + {plural_marker}")

        # 設定多個定冠詞規則
        while True:
            article_marker = input("請設定定冠詞標記（例如：the, der, la，輸入空白鍵結束）：").strip()
            if article_marker == '':  # 空白鍵結束
                break
            if article_marker:  # 只有在真的輸入內容才新增
                article_marker = article_marker + " "  # 在冠詞後加空格
                self.morphology.add_rule("definite_article", "prefix", article_marker, "定冠詞")
                print(f"已添加定冠詞規則：{article_marker}+ 詞根")


        # 生成名詞並套用定冠詞
        new_nouns = []

        def_article_rules = [r for r in self.morphology.rules if r.name == "definite_article"]
        for _ in range(3):  # 假設生成 3 個名詞
            noun_root = self.phonology.generate_word(syllable_count=random.randint(2,3))
            new_nouns.append(noun_root)

            # ✅ 展示時才加定冠詞
            if def_article_rules:
                noun_with_article = self.apply_def_article(noun_root)
                print(f"範例名詞（已套定冠詞）：{noun_with_article}")
            else:
                print(f"範例名詞：{noun_root}")

        self.vocabulary['noun'].extend(new_nouns)


        # 否定規則
        neg_prefix = input("請設定否定前綴（例如：ne，預設 ne）：").strip() or "ne"
        neg_suffix = input("請設定否定後綴（例如：pas, point, jamais，預設 pas）：").strip() or "pas"
        self.morphology.add_rule("negative", "circumfix", (neg_prefix + " ", " " + neg_suffix), "否定")
        print(f"已添加否定規則：{neg_prefix} + 動詞 + {neg_suffix}")

        # 演示構詞規則
        print("\n🎯 構詞規則演示：")
        if self.vocabulary['noun']:
            noun = random.choice(self.vocabulary['noun'])
            plural_form = self.morphology.apply_morphology(noun, "plural")
            print(f"名詞複數：{noun} → {plural_form}")

        if self.vocabulary['adjective']:
            adj = random.choice(self.vocabulary['adjective'])
            neg_form = self.morphology.apply_morphology(adj, "negative")
            print(f"形容詞否定：{adj} → {neg_form}")

        print(f"\n✅ 第二關完成！")
        self.current_level = 3


    def level_3_syntax(self):
        """第三關：設定句法系統"""
        print("\n📝 第三關：句法系統設定")
        print("-" * 40)
        print("最後，我們來設定語言的句子結構！")

        # 設定基本語序
        print("\n請選擇基本語序：")
        print("1. SVO (主語-動詞-賓語) - 如英文、中文")
        print("2. SOV (主語-賓語-動詞) - 如日文、韓文")
        print("3. VSO (動詞-主語-賓語) - 如愛爾蘭語、南島語")

        order_choice = input("請選擇 (1-3)：") or "1"

        if order_choice == "1":
            self.syntax.word_order = "SVO"
        elif order_choice == "2":
            self.syntax.word_order = "SOV"
        elif order_choice == "3":
            self.syntax.word_order = "VSO"

        print(f"已設定語序：{self.syntax.word_order}")

        # 添加句法規則
        self.syntax.add_rule("basic_sentence", self.syntax.word_order, "基本句型")

        # 疑問句規則
        question_marker = input("請設定疑問標記（例如：？, -ka, ma）：") or "ka"
        self.syntax.add_rule("question", f"{self.syntax.word_order}+{question_marker}", "疑問句")

        # 生成範例句子
        print(f"\n🎨 讓我們用 {self.syntax.word_order} 語序生成一些句子：")

        # 確保各詞類都有詞語
        if not self.vocabulary['noun']:
            self.vocabulary['noun'].append(self.phonology.generate_word())
        if not self.vocabulary['verb']:
            self.vocabulary['verb'].append(self.phonology.generate_word())

        for i in range(3):
            subject = random.choice(self.vocabulary['noun'])
            verb = random.choice(self.vocabulary['verb'])
            obj = random.choice(self.vocabulary['noun']) if len(self.vocabulary['noun']) > 1 else ""

            sentence = self.syntax.generate_sentence(subject, verb, obj)
            print(f"{i+1}. {sentence}")

            # 疑問句版本
            question_sentence = sentence + " " + question_marker
            print(f"   疑問句：{question_sentence}")

        print(f"\n✅ 第三關完成！")

    def final_showcase(self):
        """最終展示創造的語言"""
        print("\n" + "=" * 60)
        print("🎉 恭喜！你已經成功創造了一個新語言！ 🎉")
        print("=" * 60)

        print(f"\n🔤 音韻系統:")
        print(f"   子音：{', '.join(sorted(self.phonology.consonants))}")
        print(f"   母音：{', '.join(sorted(self.phonology.vowels))}")
        print(f"   音節模式：{', '.join(self.phonology.syllable_patterns)}")

        print(f"\n🔧 構詞系統:")
        for rule in self.morphology.rules:
            print(f"   {rule.name}: {rule.rule_type} '{rule.marker}' ({rule.meaning})")

        print(f"\n📝 句法系統:")
        print(f"   基本語序：{self.syntax.word_order}")
        for rule in self.syntax.rules:
            print(f"   {rule.name}: {rule.pattern}")

        print(f"\n📚 詞彙統計:")
        for word_class, words in self.vocabulary.items():
            if words and word_class != 'unknown':
                print(f"   {word_class}: {len(words)} 個詞")

        # 🔽 加入定冠詞處理邏輯 🔽
        def_article_rules = [r for r in self.morphology.rules if r.name == "definite_article"]

        subject = self.apply_def_article(random.choice(self.vocabulary['noun']))

        # 🌟 語言展示句子
        print(f"\n🌟 你的語言作品展示:")

        # 取得否定規則（circumfix）
        neg_rule = next((r for r in self.morphology.rules if r.name == "negative"), None)
        neg_prefix, neg_suffix = neg_rule.marker if neg_rule else ("", "")

        # 取得疑問標記（從語法規則中抓）
        question_rule = next((r for r in self.syntax.rules if r.name == "question"), None)
        question_marker = question_rule.pattern.split("+")[-1] if question_rule else "?"

        for i in range(3):
            if self.vocabulary['noun'] and self.vocabulary['verb']:
                subject = self.apply_def_article(random.choice(self.vocabulary['noun']))
                verb = random.choice(self.vocabulary['verb'])
                obj = self.apply_def_article(random.choice(self.vocabulary['noun'])) if len(self.vocabulary['noun']) > 1 else ""

                # 陳述句
                sentence = self.syntax.generate_sentence(subject, verb, obj)
                print(f"   陳述句：{sentence}")

                # 否定句（只否定動詞）
                negated_verb = f"{neg_prefix}{verb}{neg_suffix}".strip()
                neg_sentence = self.syntax.generate_sentence(subject, negated_verb, obj)
                print(f"   否定句：{neg_sentence}")

                # 疑問句（加問句標記）
                question_sentence = sentence + f" {question_marker}"
                print(f"   疑問句：{question_sentence}")




    def run_game(self):
        """運行遊戲主循環"""
        self.display_welcome()

        input("\n按 Enter 開始遊戲...")

        # 第一關：音韻
        if self.current_level == 1:
            self.level_1_phonology()

        # 第二關：構詞
        if self.current_level == 2:
            input("\n按 Enter 進入第二關...")
            self.level_2_morphology()

        # 第三關：句法
        if self.current_level == 3:
            input("\n按 Enter 進入第三關...")
            self.level_3_syntax()

        # 最終展示
        input("\n按 Enter 查看你創造的語言...")
        self.final_showcase()

def main():
    """主程式"""
    game = LanguageCreatorGame()
    game.run_game()

if __name__ == "__main__":
    main()