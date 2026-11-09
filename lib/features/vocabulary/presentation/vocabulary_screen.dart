import 'package:flutter/material.dart';

class VocabularyScreen extends StatelessWidget {
  const VocabularyScreen({super.key});

  static const _words = <(String, String, String)>[
    ('Hallo', 'Salom', 'Salomlashish'),
    ('Danke', 'Rahmat', 'Kundalik iboralar'),
    ('das Wasser', 'suv', 'Oziq-ovqat'),
    ('die Familie', 'oila', 'Oila'),
    ('der Freund', 'do‘st', 'Odamlar'),
    ('Guten Abend', 'Xayrli kech', 'Salomlashish'),
  ];

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(20),
      children: [
        Text('So‘zlar', style: Theme.of(context).textTheme.headlineMedium?.copyWith(fontWeight: FontWeight.bold)),
        const SizedBox(height: 6),
        const Text('Yangi so‘zlarni o‘rganing va qaytarib chiqing.'),
        const SizedBox(height: 16),
        for (final word in _words)
          Card(
            child: ListTile(
              leading: const CircleAvatar(child: Icon(Icons.volume_up_outlined)),
              title: Text(word.$1, style: const TextStyle(fontWeight: FontWeight.w700)),
              subtitle: Text('${word.$2} · ${word.$3}'),
              trailing: IconButton(onPressed: () {}, icon: const Icon(Icons.bookmark_border)),
            ),
          ),
      ],
    );
  }
}
