import 'package:flutter/material.dart';

/// "182 kunlik sayohat" sahifasi.
/// Hozircha bo'sh — keyinchalik challenge/daromad tizimi shu yerga qo'shiladi.
class JourneyScreen extends StatelessWidget {
  const JourneyScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text('182 kunlik sayohat'),
        backgroundColor: Colors.transparent,
        elevation: 0,
      ),
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(32),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Container(
                width: 88,
                height: 88,
                decoration: BoxDecoration(
                  color: theme.colorScheme.primary.withValues(alpha: 0.10),
                  borderRadius: BorderRadius.circular(28),
                ),
                child: Icon(Icons.route_rounded,
                    size: 44, color: theme.colorScheme.primary),
              ),
              const SizedBox(height: 22),
              Text(
                'Tez orada',
                style: theme.textTheme.titleLarge
                    ?.copyWith(fontWeight: FontWeight.w800),
              ),
              const SizedBox(height: 8),
              Text(
                '182 kunlik sayohat sahifasi tayyorlanmoqda.\nHar kuni bir qadam — natija o‘z-o‘zidan keladi.',
                textAlign: TextAlign.center,
                style: theme.textTheme.bodyMedium?.copyWith(
                  color: theme.colorScheme.onSurface.withValues(alpha: 0.6),
                  height: 1.6,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}