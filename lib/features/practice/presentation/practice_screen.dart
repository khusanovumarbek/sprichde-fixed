import 'package:flutter/material.dart';

class PracticeScreen extends StatefulWidget {
  const PracticeScreen({super.key});

  @override
  State<PracticeScreen> createState() => _PracticeScreenState();
}

class _PracticeScreenState extends State<PracticeScreen> {
  static const _options = ['Rahmat', 'Salom', 'Xayrli tong', 'Iltimos'];
  String? _answer;

  @override
  Widget build(BuildContext context) {
    final correct = _answer == _options[1];
    return ListView(
      padding: const EdgeInsets.all(20),
      children: [
        Text('Tezkor mashq', style: Theme.of(context).textTheme.headlineMedium?.copyWith(fontWeight: FontWeight.bold)),
        const SizedBox(height: 6),
        const Text('Nemischa so‘zning o‘zbekcha ma’nosini tanlang.'),
        const SizedBox(height: 24),
        Card(
          child: Padding(
            padding: const EdgeInsets.all(22),
            child: Column(crossAxisAlignment: CrossAxisAlignment.stretch, children: [
              const Text('“Hallo” nimani anglatadi?', style: TextStyle(fontSize: 21, fontWeight: FontWeight.w700)),
              const SizedBox(height: 18),
              for (final option in _options)
                Padding(
                  padding: const EdgeInsets.only(bottom: 9),
                  child: OutlinedButton(
                    onPressed: () => setState(() => _answer = option),
                    child: Padding(padding: const EdgeInsets.symmetric(vertical: 9), child: Text(option)),
                  ),
                ),
              if (_answer != null)
                Padding(
                  padding: const EdgeInsets.only(top: 8),
                  child: Text(correct ? 'To‘g‘ri! Barakalla 🎉' : 'Yana bir bor urinib ko‘ring.', style: TextStyle(fontWeight: FontWeight.w700, color: correct ? Colors.green : Colors.deepOrange)),
                ),
            ]),
          ),
        ),
      ],
    );
  }
}
