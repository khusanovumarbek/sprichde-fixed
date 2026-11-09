import 'package:flutter/material.dart';

import '../data/lesson_repository.dart';

class LessonsScreen extends StatelessWidget {
  const LessonsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final lessons = const LessonRepository().lessons;
    return ListView(
      padding: const EdgeInsets.all(20),
      children: [
        Text('Darslar', style: Theme.of(context).textTheme.headlineMedium?.copyWith(fontWeight: FontWeight.bold)),
        const SizedBox(height: 6),
        const Text('A1 bosqichidan boshlang va bosqichma-bosqich o‘ting.'),
        const SizedBox(height: 16),
        for (final lesson in lessons)
          Card(
            child: ListTile(
              contentPadding: const EdgeInsets.symmetric(horizontal: 18, vertical: 8),
              leading: const CircleAvatar(child: Icon(Icons.menu_book_outlined)),
              title: Text(lesson.title, style: const TextStyle(fontWeight: FontWeight.w600)),
              subtitle: Text('${lesson.level}\n${lesson.description}'),
              isThreeLine: true,
              trailing: const Icon(Icons.chevron_right),
              onTap: () => showModalBottomSheet<void>(
                context: context,
                showDragHandle: true,
                builder: (context) => SafeArea(
                  child: ListView(padding: const EdgeInsets.all(20), children: [
                    Text(lesson.title, style: Theme.of(context).textTheme.headlineSmall),
                    const SizedBox(height: 8),
                    Text(lesson.description),
                    const SizedBox(height: 16),
                    for (final word in lesson.words) ListTile(leading: const Icon(Icons.volume_up_outlined), title: Text(word)),
                  ]),
                ),
              ),
            ),
          ),
      ],
    );
  }
}
