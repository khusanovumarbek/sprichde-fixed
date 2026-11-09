import 'package:flutter/material.dart';

import 'features/home/presentation/home_screen.dart';
import 'features/lessons/presentation/lessons_screen.dart';
import 'features/practice/presentation/practice_screen.dart';
import 'features/vocabulary/presentation/vocabulary_screen.dart';

/// Kirishdan keyingi asosiy qobiq: home + bottom navigation.
class MainShell extends StatefulWidget {
  const MainShell({super.key});

  @override
  State<MainShell> createState() => _MainShellState();
}

class _MainShellState extends State<MainShell> {
  int _selectedIndex = 0;

  static const _screens = <Widget>[
    HomeScreen(),
    LessonsScreen(),
    VocabularyScreen(),
    PracticeScreen(),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(child: _screens[_selectedIndex]),
      bottomNavigationBar: NavigationBar(
        selectedIndex: _selectedIndex,
        onDestinationSelected: (index) =>
            setState(() => _selectedIndex = index),
        destinations: const [
          NavigationDestination(
              icon: Icon(Icons.home_outlined),
              selectedIcon: Icon(Icons.home),
              label: 'Bosh sahifa'),
          NavigationDestination(
              icon: Icon(Icons.menu_book_outlined),
              selectedIcon: Icon(Icons.menu_book),
              label: 'Darslar'),
          NavigationDestination(
              icon: Icon(Icons.style_outlined),
              selectedIcon: Icon(Icons.style),
              label: 'So‘zlar'),
          NavigationDestination(
              icon: Icon(Icons.quiz_outlined),
              selectedIcon: Icon(Icons.quiz),
              label: 'Mashq'),
        ],
      ),
    );
  }
}