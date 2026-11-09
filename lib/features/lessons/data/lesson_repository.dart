import '../domain/lesson.dart';

class LessonRepository {
  const LessonRepository();

  List<Lesson> get lessons => const [
        Lesson(title: 'Salomlashish', level: 'A1 · 1-dars', description: 'Nemis tilida salomlashish va tanishish.', words: ['Hallo — Salom', 'Guten Morgen — Xayrli tong', 'Wie heißt du? — Isming nima?', 'Ich heiße ... — Mening ismim ...']),
        Lesson(title: 'Kundalik tanishuv', level: 'A1 · 2-dars', description: 'O‘zingiz haqingizda sodda gaplar tuzing.', words: ['Ich komme aus ... — Men ...danman', 'Ich wohne in ... — Men ...da yashayman', 'Freut mich — Tanishganimdan xursandman']),
        Lesson(title: 'Kafe va buyurtma', level: 'A1 · 3-dars', description: 'Kafeda ichimlik va taom buyurtma qilish.', words: ['Ich möchte ... — Men ... xohlayman', 'die Speisekarte — menyu', 'Bitte — iltimos / marhamat']),
        Lesson(title: 'Oila', level: 'A1 · 4-dars', description: 'Oila a’zolari va yaqinlar haqida gapirish.', words: ['die Familie — oila', 'die Mutter — ona', 'der Bruder — aka / uka']),
      ];
}
