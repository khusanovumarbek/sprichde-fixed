import 'package:flutter/material.dart';

import 'core/theme/app_theme.dart';
import 'features/auth/presentation/auth_screen.dart';

class DeutschLernenApp extends StatelessWidget {
  const DeutschLernenApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'SprichDe',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.light,
      // Ilova kirish sahifasidan boshlanadi; kirgandan keyin MainShell ochiladi
      home: const AuthScreen(),
    );
  }
}